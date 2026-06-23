/**
 * dailyStreakApi.ts
 * ────────────────────
 * API service for Daily Streak Challenge progress tracking.
 * Communicates with the backend /api/v1/daily-streak/* endpoints.
 */

const API_BASE =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) ||
  'http://localhost:8000/api/v1';

function getHeaders(): HeadersInit {
  if (typeof window === 'undefined') return { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('accessToken');
  return {
    Authorization: token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  };
}

// ── Types ──────────────────────────────────────────────────────────────────

export interface LevelProgress {
  level_id: number;
  progress: number; // 0–100
  completed: boolean;
  locked: boolean;
}

export interface SubjectProgress {
  subject_id: string;
  levels: LevelProgress[];
}

export interface DailyStreakProgressResponse {
  subjects: SubjectProgress[];
  total_xp_earned: number;
}

export interface UpdateProgressRequest {
  subject_id: string;
  level_id: number;
  progress: number;
  completed: boolean;
}

export interface UpdateProgressResponse {
  success: boolean;
  message: string;
  subject: SubjectProgress;
  xp_earned: number;
  streak_updated: boolean;
}

// ── API Functions ──────────────────────────────────────────────────────────

/**
 * Fetch the user's progress across all 4 daily streak subjects.
 */
export async function getDailyStreakProgress(): Promise<DailyStreakProgressResponse> {
  const res = await fetch(`${API_BASE}/daily-streak/progress`, {
    method: 'GET',
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch daily streak progress');
  }
  return res.json();
}

/**
 * Update progress for a specific subject and level.
 * When completed=true, XP and streak are automatically awarded by the backend.
 */
export async function updateDailyStreakProgress(
  data: UpdateProgressRequest,
): Promise<UpdateProgressResponse> {
  const res = await fetch(`${API_BASE}/daily-streak/progress`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to update daily streak progress');
  }
  return res.json();
}
