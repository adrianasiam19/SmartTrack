/**
 * Personal Progress API client (Stages 1–5)
 */
import { fetchWithAuth } from './authApi';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export type PersonalProgressStats = {
  current_phase: number | null;
  current_phase_name: string | null;
  current_level: number | null;
  total_xp: number;
  rank: string;
  challenges_completed: number;
  learning_topics_completed: number;
  current_streak_days: number;
  longest_streak_days: number;
  overall_accuracy_pct: number | null;
  recommendations_unlocked: number;
  psychometric_completed: boolean;
  wassce_uploaded: boolean;
};

export type WeeklyProgressSummary = {
  week_start: string;
  week_end: string;
  challenges_completed: number;
  learning_topics_studied: number;
  xp_earned: number;
  xp_goal: number;
  accuracy_pct: number | null;
  learning_streak_days: number;
};

export type ProgressMeter = {
  id: string;
  label: string;
  current: number;
  target: number;
  pct: number;
  unit: string;
  detail: string | null;
};

export type ProgressVisualizations = {
  xp_progress: ProgressMeter;
  phase_progress: ProgressMeter;
  level_completion: ProgressMeter;
  challenge_accuracy: ProgressMeter;
  learning_streak: ProgressMeter;
};

export type NextGoal = {
  id: string;
  title: string;
  message: string;
  reason: string | null;
  priority: number;
  progress_current: number | null;
  progress_target: number | null;
  progress_pct: number | null;
  action_label: string | null;
  action_href: string | null;
};

export type MotivationalInsight = {
  id: string;
  message: string;
  tone: string;
  priority: number;
};

/** Stage 5 — optional future leaderboard extension (disabled in MVP). */
export type LeaderboardModuleConfig = {
  enabled: boolean;
  reason: string;
  version: number;
  mount_point: string;
  api_path: string;
  scopes: string[];
  payload: Record<string, unknown> | null;
};

export type FutureModules = {
  leaderboard: LeaderboardModuleConfig;
};

export type PersonalProgressResponse = {
  stats: PersonalProgressStats;
  weekly_summary?: WeeklyProgressSummary | null;
  visualizations?: ProgressVisualizations | null;
  next_goal?: NextGoal | null;
  insights?: MotivationalInsight[];
  future_modules?: FutureModules;
};

export async function fetchPersonalProgress(): Promise<PersonalProgressResponse> {
  const res = await fetchWithAuth(`${API_BASE}/progress/me`);
  if (!res.ok) throw new Error('Failed to load personal progress');
  return res.json();
}
