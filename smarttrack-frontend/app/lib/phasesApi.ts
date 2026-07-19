/**
 * Phase / Level progression API client
 */
import { fetchWithAuth } from './authApi';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

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
