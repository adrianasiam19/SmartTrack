/**
 * starterArenaApi.ts
 * ──────────────────
 * API client for the redesigned adaptive Starter Arena.
 * Communicates with the backend starter-arena endpoints.
 */

const API_BASE_URL =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) ||
  'http://localhost:8000/api/v1';

const getAuthHeaders = (): HeadersInit => {
  if (typeof window === 'undefined') return { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('accessToken');
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

// ── Types ─────────────────────────────────────────────────────────────────

export interface StarterQuestion {
  id: string;
  type: 'psychometric' | 'academic';
  question: string;
  options: Record<string, string> | Array<{ value: string; label: string }>;
  domain?: string;
  category?: string;
  display?: string;
  correct_key?: string;
  explanation?: string;
}

export interface StartSessionResponse {
  session_id: string;
  questions: StarterQuestion[];
  total_count: number;
}

export interface LearnerProfile {
  learning_style: {
    primary: string;
    description: string;
  };
  academic_strengths: string[];
  academic_weaknesses: string[];
  confidence_level: string;
  reasoning_ability: string;
  recommended_focus: string;
  recommended_challenges: string[];
  recommendation_profile: string;
}

export interface CompleteSessionResponse {
  success: boolean;
  profile?: LearnerProfile;
  error?: string;
}

export interface StoredResponse {
  question_id: string;
  question: string;
  type: 'psychometric' | 'academic';
  answer: string;
  correct?: boolean;
  domain?: string;
  time_taken: number;
}

// ── API Functions ─────────────────────────────────────────────────────────

/**
 * Start a new Starter Arena session with mixed psychometric + academic questions.
 */
export async function startStarterArena(
  psychometricCount: number = 6,
  academicCount: number = 6
): Promise<StartSessionResponse> {
  const response = await fetch(`${API_BASE_URL}/starter-arena/start`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      psychometric_count: psychometricCount,
      academic_count: academicCount,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to start Starter Arena');
  }

  return response.json();
}

/**
 * Complete the Starter Arena and generate a learner profile.
 */
export async function completeStarterArena(
  sessionId: string,
  psychometricResponses: StoredResponse[],
  academicResponses: StoredResponse[]
): Promise<CompleteSessionResponse> {
  const response = await fetch(`${API_BASE_URL}/starter-arena/complete`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      session_id: sessionId,
      psychometric_responses: psychometricResponses,
      academic_responses: academicResponses,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    return {
      success: false,
      error: error.detail || 'Failed to complete Starter Arena',
    };
  }

  return response.json();
}
