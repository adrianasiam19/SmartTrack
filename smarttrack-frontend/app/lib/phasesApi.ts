/**
 * Phase / Level progression API client
 */
import { fetchWithAuth } from './authApi';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/** Must match backend Settings.CHALLENGE_FORMAT_VERSION — stale sessions are regenerated. */
export const CHALLENGE_FORMAT_VERSION = 10;

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
  const res = await fetchWithAuth(`${API_BASE}/phases/me`);
  if (!res.ok) throw new Error('Failed to load progression');
  return res.json();
}

export async function startLevel(levelId: number) {
  const res = await fetchWithAuth(`${API_BASE}/phases/levels/${levelId}/start`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to start level');
  }
  return res.json();
}

export async function replayLevel(levelId: number) {
  const res = await fetchWithAuth(`${API_BASE}/phases/levels/${levelId}/replay`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to replay level');
  return res.json();
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

/**
 * If the cached play session predates mixed question types / images,
 * start or replay the level again so every attempt uses the new format.
 */
export async function refreshPhaseSessionIfStale(): Promise<Record<string, unknown> | null> {
  const cached = readPhaseSession();
  if (isFreshPhaseSession(cached)) return cached;

  const levelId = Number(cached?.level_id);
  if (!Number.isFinite(levelId) || levelId <= 0) {
    sessionStorage.removeItem('atlasPhaseSession');
    return null;
  }

  const preferReplay = Boolean(cached?.is_replay);
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

export async function completePhaseSession(sessionId: number) {
  const res = await fetchWithAuth(
    `${API_BASE}/phases/sessions/${sessionId}/complete`,
    { method: 'POST' },
  );
  if (!res.ok) throw new Error('Failed to complete session');
  return res.json() as Promise<{
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
  }>;
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
