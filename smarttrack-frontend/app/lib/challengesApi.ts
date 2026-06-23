/**
 * challengesApi.ts
 * ──────────────────
 * API utilities for the Phase 2 Challenge & Learning System.
 * Handles all communication with the backend challenges endpoints.
 */

const API_BASE =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) ||
  'http://localhost:8000/api/v1';

const getHeaders = (): HeadersInit => {
  if (typeof window === 'undefined') return { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('accessToken');
  return {
    Authorization: token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  };
};

// ── Question Types ─────────────────────────────────────────────────────────

/** Supported interaction modes for questions */
export type QuestionType =
  | 'mcq'           // Standard multiple-choice
  | 'fill-blank'    // Fill in the blank
  | 'predict'       // Pattern prediction with reveal
  | 'match'         // Drag-and-drop matching
  | 'rank'          // Order/ranking
  | 'scenario'      // Scenario-based decision
  | 'discover';     // Click-to-discover card

export interface Question {
  id: number;
  domain: string;
  question: string;
  options: { [key: string]: string };
  answer_hash: string;
  /** Interaction type — defaults to 'mcq' for existing questions */
  question_type?: QuestionType;
  /** Extra metadata (optional, used by local arena data) */
  _category?: string;
  _mission?: string;
  _explanation?: string;
  _xp?: number;
  /** For fill-blank: expected answer(s) */
  _answers?: string[];
  /** For fill-blank: hints */
  _hints?: string[];
  /** For pattern predict: the pattern string to show */
  _pattern?: string;
  /** For match: left items */
  _leftItems?: string[];
  /** For match: right items */
  _rightItems?: string[];
  /** For match: correct mapping leftIndex -> rightIndex */
  _correctMatches?: number[];
  /** For rank: items in correct order */
  _rankedOrder?: string[];
  /** For scenario: can select multiple options */
  _allowMultiple?: boolean;
}

export interface SubmitResponse {
  xp_gained: number;
  streak_updated: number;
  level_up: boolean;
  new_rank: string | null;
  next_questions: Question[];
  behavioural_traits?: Record<string, number>;
}

export interface CalibrationStartResponse {
  session_id: string;
  questions: Question[];
}

export interface LearningModule {
  id: number;
  domain: string;
  title: string;
  content: string;
  difficulty_level: number;
}

export interface UserProgress {
  xp: number;
  rank: string;
  streak: number;
  level: number;
  xp_for_next_level: number;
  xp_progress: number;
}

export interface BehaviourData {
  retries: number;
  response_time_avg: number;
  preferred_domain: string;
  consistency: number;
  persistence: number;
}

export interface PsychometricAnswer {
  question_id: string;
  answer: string;
}

export interface LeaderboardEntry {
  rank: number;
  user_name: string;
  xp: number;
  streak: number;
  school: string;
  programme: string;
  is_me?: boolean;
}

export interface ChallengeCategory {
  id: string;
  title: string;
  description: string;
  icon: string; // emoji or icon name
  domain: string;
  /** Maps to the question bank arena: "logic" | "quantitative" | "scientific" | "communication" | "mixed" */
  arena?: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  colour: string; // gradient class
  estimated_time: string;
  programme: 'Science' | 'Arts' | 'Both';
  /** SHS levels this category is appropriate for */
  shsLevels?: ('SHS 1' | 'SHS 2' | 'SHS 3')[];
}

// ── Challenge Categories ──────────────────────────────────────────────────
//
// Each category maps directly to one of the 4 arenas in the question bank:
//   - Logic Arena          → arena:"logic"
//   - Quantitative Sprint  → arena:"quantitative"
//   - Scientific Thinking  → arena:"scientific"
//   - Communication Arena  → arena:"communication"
//
// Each arena is further subdivided into difficulty tiers:
//   Bronze  (SHS 1),  Silver  (SHS 1-2),  Gold  (SHS 2-3)

// ── Helper: tier name for display & filtering ──
export function tierLabel(tier: string): string {
  const labels: Record<string, string> = {
    Bronze: '🥉 Bronze',
    Silver: '🥈 Silver',
    Gold:   '🥇 Gold',
  };
  return labels[tier] || tier;
}

export function tierSHSLevels(tier: string): ("SHS 1" | "SHS 2" | "SHS 3")[] {
  const map: Record<string, ("SHS 1" | "SHS 2" | "SHS 3")[]> = {
    Bronze: ['SHS 1'],
    Silver: ['SHS 1', 'SHS 2'],
    Gold:   ['SHS 2', 'SHS 3'],
  };
  return map[tier] || ['SHS 1', 'SHS 2', 'SHS 3'];
}

export const SCIENCE_CATEGORIES: ChallengeCategory[] = [
  {
    id: 'logic-arena',
    title: '🧠 Logic Arena',
    description: 'Spot patterns, solve syllogisms, and master deductive reasoning challenges from Brilliant.org-style puzzles.',
    icon: '🧠',
    domain: 'Logic',
    arena: 'logic',
    difficulty: 'Intermediate',
    colour: 'from-violet-500/20 to-purple-500/20',
    estimated_time: '5 min',
    programme: 'Science',
    shsLevels: ['SHS 1', 'SHS 2', 'SHS 3'],
  },
  {
    id: 'scientific-thinking',
    title: '🔬 Scientific Thinking',
    description: 'Think like a scientist — hypothesize, interpret observations, and draw evidence-backed conclusions.',
    icon: '🔬',
    domain: 'Science',
    arena: 'scientific',
    difficulty: 'Intermediate',
    colour: 'from-cyan-500/20 to-blue-500/20',
    estimated_time: '5 min',
    programme: 'Science',
    shsLevels: ['SHS 1', 'SHS 2', 'SHS 3'],
  },
  {
    id: 'quantitative-sprint',
    title: '📊 Quantitative Sprint',
    description: 'Quick-fire numerical reasoning — ratios, percentages, speed, interest, and mental math challenges.',
    icon: '📊',
    domain: 'Math',
    arena: 'quantitative',
    difficulty: 'Beginner',
    colour: 'from-emerald-500/20 to-teal-500/20',
    estimated_time: '3 min',
    programme: 'Science',
    shsLevels: ['SHS 1', 'SHS 2'],
  },
  {
    id: 'advanced-quantitative',
    title: '📈 Advanced Quantitative',
    description: 'Algebra, geometry, interest, probability — harder quantitative challenges for Gold-tier students.',
    icon: '📈',
    domain: 'Math',
    arena: 'quantitative',
    difficulty: 'Advanced',
    colour: 'from-indigo-500/20 to-violet-500/20',
    estimated_time: '8 min',
    programme: 'Science',
    shsLevels: ['SHS 2', 'SHS 3'],
  },
  {
    id: 'communication-arena',
    title: '💬 Communication Arena',
    description: 'Read passages, interpret meaning, analyse arguments, and express ideas with clarity and precision.',
    icon: '💬',
    domain: 'Verbal',
    arena: 'communication',
    difficulty: 'Beginner',
    colour: 'from-rose-500/20 to-pink-500/20',
    estimated_time: '5 min',
    programme: 'Science',
    shsLevels: ['SHS 1', 'SHS 2'],
  },
];

export const ARTS_CATEGORIES: ChallengeCategory[] = [
  {
    id: 'communication-arena',
    title: '💬 Communication Arena',
    description: 'Read passages, interpret meaning, analyse arguments, and express ideas with clarity and precision.',
    icon: '💬',
    domain: 'Verbal',
    arena: 'communication',
    difficulty: 'Beginner',
    colour: 'from-rose-500/20 to-pink-500/20',
    estimated_time: '5 min',
    programme: 'Arts',
    shsLevels: ['SHS 1', 'SHS 2'],
  },
  {
    id: 'critical-thinking',
    title: '⚖️ Critical Thinking',
    description: 'Analyze arguments, evaluate evidence, spot assumptions, and form reasoned judgments.',
    icon: '⚖️',
    domain: 'Logic',
    arena: 'communication',
    difficulty: 'Intermediate',
    colour: 'from-amber-500/20 to-orange-500/20',
    estimated_time: '5 min',
    programme: 'Arts',
    shsLevels: ['SHS 1', 'SHS 2', 'SHS 3'],
  },
  {
    id: 'advanced-reasoning',
    title: '🧩 Advanced Reasoning',
    description: 'Complex scenarios, decision trade-offs, and argument analysis for advanced students.',
    icon: '🧩',
    domain: 'General',
    arena: 'communication',
    difficulty: 'Advanced',
    colour: 'from-sky-500/20 to-blue-500/20',
    estimated_time: '8 min',
    programme: 'Arts',
    shsLevels: ['SHS 2', 'SHS 3'],
  },
];

export const SHARED_CATEGORIES: ChallengeCategory[] = [
  {
    id: 'problem-solving',
    title: '🎯 Problem Solving',
    description: 'Tackle real-world problems with creative and structured quantitative thinking.',
    icon: '🎯',
    domain: 'Math',
    arena: 'quantitative',
    difficulty: 'Advanced',
    colour: 'from-red-500/20 to-rose-500/20',
    estimated_time: '8 min',
    programme: 'Both',
    shsLevels: ['SHS 2', 'SHS 3'],
  },
];

// ── Unified Challenge Categories ──────────────────────────────────────────
// All students see the same 4 core arenas. Content (questions) differs by
// programme at the backend level, but the frontend card structure is universal.

export const ALL_CHALLENGE_CATEGORIES: ChallengeCategory[] = [
  {
    id: 'logic-arena',
    title: '🧠 Logic Arena',
    description: 'Spot patterns, solve syllogisms, and master deductive reasoning challenges from Brilliant.org-style puzzles.',
    icon: '🧠',
    domain: 'Logic',
    arena: 'logic',
    difficulty: 'Intermediate',
    colour: 'from-violet-500/20 to-purple-500/20',
    estimated_time: '5 min',
    programme: 'Both',
    shsLevels: ['SHS 1', 'SHS 2', 'SHS 3'],
  },
  {
    id: 'quantitative-sprint',
    title: '📊 Quantitative Sprint',
    description: 'Quick-fire numerical reasoning — ratios, percentages, speed, interest, and mental math challenges.',
    icon: '📊',
    domain: 'Math',
    arena: 'quantitative',
    difficulty: 'Beginner',
    colour: 'from-emerald-500/20 to-teal-500/20',
    estimated_time: '3 min',
    programme: 'Both',
    shsLevels: ['SHS 1', 'SHS 2'],
  },
  {
    id: 'communication-arena',
    title: '💬 Communication Arena',
    description: 'Read passages, interpret meaning, analyse arguments, and express ideas with clarity and precision.',
    icon: '💬',
    domain: 'Verbal',
    arena: 'communication',
    difficulty: 'Beginner',
    colour: 'from-rose-500/20 to-pink-500/20',
    estimated_time: '5 min',
    programme: 'Both',
    shsLevels: ['SHS 1', 'SHS 2'],
  },
  {
    id: 'scientific-thinking',
    title: '🔬 Scientific Thinking',
    description: 'Think like a scientist — hypothesize, interpret observations, and draw evidence-backed conclusions.',
    icon: '🔬',
    domain: 'Science',
    arena: 'scientific',
    difficulty: 'Intermediate',
    colour: 'from-cyan-500/20 to-blue-500/20',
    estimated_time: '5 min',
    programme: 'Both',
    shsLevels: ['SHS 1', 'SHS 2', 'SHS 3'],
  },
];

// The Starter Arena — a special entry-level discovery experience
export const STARTER_ARENA: ChallengeCategory = {
  id: 'starter-arena',
  title: '🌟 Starter Arena',
  description: 'A friendly discovery journey! Atlas will learn about your strengths, interests, and thinking style through fun challenges and activities.',
  icon: '🌟',
  domain: 'General',
  arena: 'mixed',
  difficulty: 'Beginner',
  colour: 'from-indigo-500/20 to-purple-500/20',
  estimated_time: '10 min',
  programme: 'Both',
};

// ── Psychometric prompts injected between challenges ─────────────────────

export const PSYCHOMETRIC_PROMPTS = [
  {
    id: 'psych_q1',
    question: 'What activities do you enjoy most?',
    options: [
      { value: 'A', label: 'Solving puzzles & brain teasers' },
      { value: 'B', label: 'Reading & creative writing' },
      { value: 'C', label: 'Building things with my hands' },
      { value: 'D', label: 'Discussing ideas with friends' },
    ],
  },
  {
    id: 'psych_q2',
    question: 'Would you rather:',
    options: [
      { value: 'A', label: 'Solve technical problems' },
      { value: 'B', label: 'Lead and inspire people' },
      { value: 'C', label: 'Create designs and art' },
      { value: 'D', label: 'Analyze data and trends' },
    ],
  },
  {
    id: 'psych_q3',
    question: 'When studying, you prefer:',
    options: [
      { value: 'A', label: 'Step-by-step instructions' },
      { value: 'B', label: 'Group discussions' },
      { value: 'C', label: 'Visual diagrams & videos' },
      { value: 'D', label: 'Hands-on practice' },
    ],
  },
  {
    id: 'psych_q4',
    question: 'What describes you best?',
    options: [
      { value: 'A', label: 'Curious and analytical' },
      { value: 'B', label: 'Creative and imaginative' },
      { value: 'C', label: 'Organized and reliable' },
      { value: 'D', label: 'Adventurous and bold' },
    ],
  },
  {
    id: 'psych_q5',
    question: 'In a group project, you usually:',
    options: [
      { value: 'A', label: 'Plan and organize the work' },
      { value: 'B', label: 'Present and communicate findings' },
      { value: 'C', label: 'Research and gather data' },
      { value: 'D', label: 'Build and create the final product' },
    ],
  },
];

// ── API Functions ─────────────────────────────────────────────────────────

/** Start a calibration / placement match session */
export async function startCalibration(domain?: string, shsLevel?: string): Promise<CalibrationStartResponse> {
  const params = new URLSearchParams();
  if (domain) params.set('domain', domain);
  if (shsLevel) params.set('shs_level', shsLevel);
  const query = params.toString();
  const url = `${API_BASE}/challenges/calibration/start${query ? `?${query}` : ''}`;

  const res = await fetch(url, { method: 'POST', headers: getHeaders() });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to start calibration');
  }
  return res.json();
}

/** Fetch the next question (background prefetch) */
export async function fetchNextQuestions(domain?: string, shsLevel?: string): Promise<Question[]> {
  const params = new URLSearchParams();
  if (domain) params.set('domain', domain);
  if (shsLevel) params.set('shs_level', shsLevel);
  const query = params.toString();
  const url = `${API_BASE}/challenges/question/next${query ? `?${query}` : ''}`;
  const res = await fetch(url, { headers: getHeaders() });
  if (!res.ok) return [];
  const data = await res.json();
  return data.questions || [];
}

/** Submit an answer and get XP, streak, next questions */
export async function submitAnswer(params: {
  question_id: number;
  selected_option: string;
  time_taken_seconds: number;
  hints_used: number;
  is_correct: boolean;
}): Promise<SubmitResponse> {
  const res = await fetch(`${API_BASE}/challenges/response/submit`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to submit answer');
  }
  return res.json();
}

/** Fetch ONE random psychometric insight card from the backend */
export async function fetchPsychometricCard(): Promise<{
  id: string;
  category: string;
  question: string;
  display: string;
  options: { value: string; label: string }[];
} | null> {
  try {
    const res = await fetch(`${API_BASE}/challenges/psychometric/card`, {
      headers: getHeaders(),
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

/** Submit a psychometric answer */
export async function submitPsychometric(data: PsychometricAnswer): Promise<void> {
  await fetch(`${API_BASE}/challenges/psychometric`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  }).catch(() => {
    // Silently fail — psychometric submission is non-critical
    console.warn('Failed to submit psychometric response');
  });
}

/** Get user's challenge progress */
export async function getUserProgress(): Promise<UserProgress> {
  const res = await fetch(`${API_BASE}/challenges/progress`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch progress');
  return res.json();
}

/** Get leaderboard entries */
export async function getLeaderboard(
  category: string = 'Overall',
  programme?: string
): Promise<LeaderboardEntry[]> {
  const params = new URLSearchParams();
  if (category) params.set('category', category);
  if (programme) params.set('programme', programme);

  const res = await fetch(`${API_BASE}/challenges/leaderboard?${params.toString()}`, {
    headers: getHeaders(),
  });
  if (!res.ok) return [];
  return res.json();
}

/** Get learning modules */
export async function getRecommendedModules(): Promise<{
  modules: LearningModule[];
  user_theta: Record<string, number>;
}> {
  const res = await fetch(`${API_BASE}/challenges/learning/modules/recommended`, {
    headers: getHeaders(),
  });
  if (!res.ok) throw new Error('Failed to load learning modules');
  return res.json();
}

/** Get challenge completion status */
export async function getChallengeStatus(): Promise<{
  academic_completed: boolean;
  psychometric_completed: boolean;
  is_fully_completed: boolean;
  last_updated: string;
}> {
  const res = await fetch(`${API_BASE}/challenges/completion-status`, { headers: getHeaders() });
  if (!res.ok) {
    return { academic_completed: false, psychometric_completed: false, is_fully_completed: false, last_updated: '' };
  }
  return res.json();
}

/** Get challenge score */
export async function getChallengeScore(): Promise<{
  score_percentage: number;
  performance_level: string;
  total_questions: number;
  correct_answers: number;
}> {
  const res = await fetch(`${API_BASE}/challenges/score`, { headers: getHeaders() });
  if (!res.ok) throw new Error('Failed to fetch score');
  return res.json();
}

/** Update user profile (programme, level, school) */
export async function updateProfile(data: {
  programme?: string;
  shs_level?: string;
  school?: string;
}): Promise<void> {
  const res = await fetch(`${API_BASE}/users/me`, {
    method: 'PATCH',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update profile');
}

/** Submit behavioural telemetry at session end */
export async function submitBehaviourData(data: {
  session_id?: string;
  retries: number;
  response_time_avg: number;
  response_times: number[];
  questions_answered: number;
  correct_answers: number;
  consistency: number;
  domain?: string;
}): Promise<void> {
  // Fire-and-forget — non-critical data for future recommendation intelligence.
  // Backend endpoint will be fully wired in Phase 3.
  await fetch(`${API_BASE}/challenges/behaviour`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  }).catch(() => {
    console.warn('Behaviour tracking submission failed (expected if endpoint not yet deployed)');
  });
}
