/**
 * Phase / Level progression API client
 */
import { fetchWithAuth, getFetchErrorMessage, formatApiDetail } from './authApi';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function readApiError(res: Response, fallback: string): Promise<string> {
  const err = await res.json().catch(() => ({}));
  return formatApiDetail((err as { detail?: unknown }).detail, fallback);
}

/** Must match backend Settings.CHALLENGE_FORMAT_VERSION — stale sessions are regenerated. */
export const CHALLENGE_FORMAT_VERSION = 12;

export type LevelPublic = {
  id: number;
  number: number;
  difficulty_baseline: number;
  status: string;
  score?: number | null;
  attempts: number;
  completed_at?: string | null;
};

export type PhasePublic = {
  id: number;
  number: number;
  name: string;
  description?: string | null;
  status: string;
  levels: LevelPublic[];
};

export type ProgressionMe = {
  phases: PhasePublic[];
  current_phase_number: number;
  current_level_number: number;
};

export async function getProgression(): Promise<ProgressionMe> {
  try {
    const res = await fetchWithAuth(`${API_BASE}/phases/me`);
    if (!res.ok) throw new Error(await readApiError(res, 'Failed to load progression'));
    return res.json();
  } catch (err) {
    throw new Error(getFetchErrorMessage(err));
  }
}

export async function startLevel(levelId: number) {
  try {
    const res = await fetchWithAuth(`${API_BASE}/phases/levels/${levelId}/start`, {
      method: 'POST',
      signal: AbortSignal.timeout(120_000),
    });
    if (!res.ok) {
      throw new Error(await readApiError(res, 'Failed to start level'));
    }
    return res.json();
  } catch (err) {
    if (err instanceof DOMException && err.name === 'TimeoutError') {
      throw new Error(
        'Starting this level is taking too long. Check your connection and try again.',
      );
    }
    throw new Error(getFetchErrorMessage(err));
  }
}

export async function replayLevel(levelId: number) {
  try {
    const res = await fetchWithAuth(`${API_BASE}/phases/levels/${levelId}/replay`, {
      method: 'POST',
      signal: AbortSignal.timeout(120_000),
    });
    if (!res.ok) throw new Error(await readApiError(res, 'Failed to replay level'));
    return res.json();
  } catch (err) {
    if (err instanceof DOMException && err.name === 'TimeoutError') {
      throw new Error(
        'Replaying this level is taking too long. Check your connection and try again.',
      );
    }
    throw new Error(getFetchErrorMessage(err));
  }
}

export type PrefetchStatus = {
  status: 'idle' | 'fetching' | 'ready' | 'error' | string;
  level_id?: number | null;
  format_version?: number | null;
  question_count?: number;
  error?: string | null;
  cached_level_id?: number | null;
  ready_levels?: number[];
  fetching_levels?: number[];
  buffer_size?: number;
};

export type WarmPrefetchResult = {
  status: string;
  warmed: number[];
  ready_count: number;
  fetching_count: number;
  question_count: number;
  ready_levels?: number[];
  fetching_levels?: number[];
};

/** Kick off background generation for a level (usually the next one). */
export async function prefetchLevel(levelId: number): Promise<PrefetchStatus> {
  const res = await fetchWithAuth(`${API_BASE}/phases/levels/${levelId}/prefetch`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to prefetch level');
  }
  return res.json();
}

/**
 * Top up the rolling challenge buffer (next ~2–3 levels) in the background.
 * Call from Dashboard / Challenges so Start can feel instant.
 */
export async function warmPrefetchBuffer(
  anchorLevelId?: number | null,
): Promise<WarmPrefetchResult> {
  const qs =
    anchorLevelId != null && Number.isFinite(anchorLevelId)
      ? `?anchor_level_id=${anchorLevelId}`
      : '';
  const res = await fetchWithAuth(`${API_BASE}/phases/prefetch/warm${qs}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to warm challenge buffer');
  }
  return res.json();
}

export async function getPrefetchStatus(levelId: number): Promise<PrefetchStatus> {
  const res = await fetchWithAuth(
    `${API_BASE}/phases/levels/${levelId}/prefetch-status`,
  );
  if (!res.ok) throw new Error('Failed to load prefetch status');
  return res.json();
}

/** Find the next level id within the same phase (or null at phase end). */
export function findNextLevelId(
  phases: PhasePublic[],
  currentLevelId: number,
): { id: number; number: number } | null {
  for (const phase of phases) {
    const idx = phase.levels.findIndex((l) => l.id === currentLevelId);
    if (idx < 0) continue;
    const next = phase.levels[idx + 1];
    if (next) return { id: next.id, number: next.number };
    return null;
  }
  return null;
}

/** Persist session and ensure it uses the current adaptive challenge format. */
export function storePhaseSession(session: Record<string, unknown>) {
  const stamped = {
    ...session,
    format_version:
      typeof session.format_version === 'number'
        ? session.format_version
        : CHALLENGE_FORMAT_VERSION,
  };
  sessionStorage.setItem('atlasPhaseSession', JSON.stringify(stamped));
  return stamped;
}

export function readPhaseSession(): Record<string, unknown> | null {
  const raw = sessionStorage.getItem('atlasPhaseSession');
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return null;
  }
}

export function isFreshPhaseSession(session: Record<string, unknown> | null): boolean {
  if (!session) return false;
  return Number(session.format_version) === CHALLENGE_FORMAT_VERSION;
}

export type PhaseSessionStatus = {
  session_id: number;
  status: string;
  level_id?: number | null;
  is_replay?: boolean;
  answered_count?: number;
  question_count?: number;
};

export async function getPhaseSessionStatus(
  sessionId: number,
): Promise<PhaseSessionStatus> {
  const res = await fetchWithAuth(`${API_BASE}/phases/sessions/${sessionId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail =
      typeof err?.detail === 'string' ? err.detail : `Session status failed (${res.status})`;
    throw new Error(detail);
  }
  return res.json() as Promise<PhaseSessionStatus>;
}

/**
 * Ensure the cached play session is still active on the server.
 * Completed sessions must NOT restart at Q1 — that wiped progression in production
 * when complete was slow and the tab remounted / retried.
 */
export async function refreshPhaseSessionIfStale(): Promise<Record<string, unknown> | null> {
  const cached = readPhaseSession();
  const levelId = Number(cached?.level_id);
  const sessionId = Number(cached?.session_id);
  const preferReplay = Boolean(cached?.is_replay);

  const restart = async (): Promise<Record<string, unknown> | null> => {
    if (!Number.isFinite(levelId) || levelId <= 0) {
      sessionStorage.removeItem('atlasPhaseSession');
      return null;
    }
    try {
      const fresh = preferReplay
        ? await replayLevel(levelId)
        : await startLevel(levelId);
      return storePhaseSession(fresh);
    } catch {
      try {
        const fresh = await startLevel(levelId);
        return storePhaseSession(fresh);
      } catch {
        sessionStorage.removeItem('atlasPhaseSession');
        return null;
      }
    }
  };

  if (!isFreshPhaseSession(cached)) {
    return restart();
  }

  if (!Number.isFinite(sessionId) || sessionId <= 0) {
    return restart();
  }

  try {
    const status = await getPhaseSessionStatus(sessionId);
    if (status.status === 'completed') {
      return { ...cached, status: 'completed' };
    }
    if (status.status !== 'in_progress') {
      return restart();
    }
    return cached;
  } catch {
    // Transient network blip — keep the cached in-progress session.
    return cached;
  }
}

/**
 * Only for genuinely abandoned mid-level sessions.
 * Do not use after the last question / completed session.
 */
export async function recoverPhaseSession(
  levelId: number,
  isReplay = false,
): Promise<Record<string, unknown>> {
  const fresh = isReplay ? await replayLevel(levelId) : await startLevel(levelId);
  return storePhaseSession(fresh);
}

export async function submitPhaseAnswer(
  sessionId: number,
  questionId: number,
  answer: string,
  timeTakenSeconds?: number,
) {
  const res = await fetchWithAuth(
    `${API_BASE}/phases/sessions/${sessionId}/submit-answer`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_id: questionId,
        answer,
        time_taken_seconds: timeTakenSeconds ?? null,
      }),
    },
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail =
      typeof err?.detail === 'string'
        ? err.detail
        : Array.isArray(err?.detail)
          ? err.detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join(', ')
          : null;
    throw new Error(detail || `Failed to submit answer (${res.status})`);
  }
  return res.json() as Promise<{
    is_correct: boolean;
    explanation?: string;
    correct_count: number;
    wrong_count: number;
    xp_earned: number;
    user_xp?: number;
    rank?: string;
    streak?: number;
    streak_incremented?: boolean;
    learning_nudge?: {
      subject: string;
      message?: string;
      curriculum_id?: string | null;
      topic_title?: string | null;
    } | null;
  }>;
}

export type CompletePhaseResult = {
  passed: boolean;
  score: number;
  threshold: number;
  level_completed: boolean;
  next?: string | null;
  phase_number?: number | null;
  level_id?: number | null;
  next_level_id?: number | null;
  next_level_number?: number | null;
  session_xp?: number;
  user_xp?: number;
  rank?: string;
  streak?: number;
  streak_incremented?: boolean;
  learning_nudge?: {
    subject: string;
    message?: string;
    curriculum_id?: string | null;
    topic_title?: string | null;
  } | null;
};

export async function completePhaseSession(sessionId: number): Promise<CompletePhaseResult> {
  const res = await fetchWithAuth(
    `${API_BASE}/phases/sessions/${sessionId}/complete`,
    {
      method: 'POST',
      signal: AbortSignal.timeout(60_000),
    },
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail =
      typeof err?.detail === 'string'
        ? err.detail
        : `Failed to complete session (${res.status})`;
    throw new Error(detail);
  }
  return res.json() as Promise<CompletePhaseResult>;
}

/** Retry complete — server is idempotent; production often drops the first response. */
export async function completePhaseSessionWithRetry(
  sessionId: number,
  attempts = 3,
): Promise<CompletePhaseResult> {
  let lastError: Error | null = null;
  for (let i = 0; i < attempts; i++) {
    try {
      return await completePhaseSession(sessionId);
    } catch (e) {
      lastError = e instanceof Error ? e : new Error('Failed to complete session');
      if (i < attempts - 1) {
        await new Promise((r) => setTimeout(r, 800 * (i + 1)));
      }
    }
  }
  throw lastError || new Error('Failed to complete session');
}

export async function startCheckpoint(phaseNumber: number) {
  const res = await fetchWithAuth(
    `${API_BASE}/psychometrics/checkpoint/${phaseNumber}/start`,
    { method: 'POST' },
  );
  if (!res.ok) throw new Error('Failed to start checkpoint');
  return res.json();
}

export async function answerCheckpoint(
  phaseNumber: number,
  questionId: number,
  optionId: number,
) {
  const res = await fetchWithAuth(
    `${API_BASE}/psychometrics/checkpoint/${phaseNumber}/answer`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_id: questionId, option_id: optionId }),
    },
  );
  if (!res.ok) throw new Error('Failed to save answer');
  return res.json();
}

export async function completeCheckpoint(phaseNumber: number) {
  const res = await fetchWithAuth(
    `${API_BASE}/psychometrics/checkpoint/${phaseNumber}/complete`,
    { method: 'POST' },
  );
  if (!res.ok) throw new Error('Failed to complete checkpoint');
  return res.json();
}

export async function getRecommendationHistory() {
  const res = await fetchWithAuth(`${API_BASE}/recommendations/history`);
  if (!res.ok) throw new Error('Failed to load recommendations');
  return res.json();
}

export type RecommendationEligibility = {
  eligible: boolean;
  title: string;
  message: string;
  short_message: string;
  all_phases_completed?: boolean;
  wassce_optional?: boolean;
  wassce_recommended_now?: boolean;
  wassce_on_file?: boolean;
  mandatory: {
    all_levels_in_a_phase_completed: boolean;
    phases_completed_levels: number[];
    focus_phase: {
      number: number;
      name: string;
      levels_completed: number;
      levels_total: number;
      levels_remaining: number;
    } | null;
  };
  recommended: {
    learning_center_lesson_completed: boolean;
    required: boolean;
    completed_lesson_count: number;
  };
  phases: Array<{
    phase_number: number;
    phase_name: string;
    levels_completed: number;
    levels_total: number;
    all_levels_completed: boolean;
  }>;
};

export async function getRecommendationEligibility(): Promise<RecommendationEligibility> {
  const res = await fetchWithAuth(`${API_BASE}/recommendations/eligibility`);
  if (!res.ok) throw new Error('Failed to load recommendation eligibility');
  return res.json();
}
