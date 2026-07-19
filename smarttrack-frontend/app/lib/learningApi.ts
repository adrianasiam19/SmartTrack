import { getAccessToken } from './authApi';

const API_BASE_URL =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) ||
  'http://localhost:8000/api/v1';

export interface CurriculumTopic {
  curriculum_id: string;
  title: string;
  subject: string;
  shs_level: string;
  estimated_minutes: number;
  difficulty: number;
  xp_reward: number;
  reason?: string | null;
}

export interface WorkedExample {
  title: string;
  steps: string[];
  answer: string;
}

export interface AITaughtLesson {
  topic_title: string;
  simple_introduction: string;
  main_explanation: string;
  step_by_step_examples: WorkedExample[];
  real_life_applications: string[];
  important_points: string[];
  common_mistakes: string[];
  short_summary: string;
}

export interface TaughtLessonResponse {
  curriculum_id: string;
  subject: string;
  shs_level: string;
  estimated_minutes: number;
  xp_reward: number;
  lesson: AITaughtLesson;
}

export interface TutorMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface LibraryHome {
  continue_learning: CurriculumTopic | null;
  recommended: CurriculumTopic[];
  recent: CurriculumTopic[];
  bookmarks: CurriculumTopic[];
}

function authHeaders(): HeadersInit {
  const token = getAccessToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function readError(response: Response, fallback: string): Promise<Error> {
  if (response.status === 401) {
    return new Error('Your session expired. Please sign in again, then retry.');
  }
  const body = await response.json().catch(() => null);
  const detail = body?.detail;
  if (typeof detail === 'string' && detail.trim()) {
    if (/could not validate credentials/i.test(detail)) {
      return new Error('Your session expired. Please sign in again, then retry.');
    }
    return new Error(detail);
  }
  return new Error(fallback);
}

export async function searchCurriculumTopics(
  query: string,
  signal?: AbortSignal,
  subject?: string,
): Promise<CurriculumTopic[]> {
  const params = new URLSearchParams({ q: query, limit: '20' });
  if (subject) params.set('subject', subject);
  const response = await fetch(`${API_BASE_URL}/learning/search?${params}`, {
    headers: authHeaders(),
    signal,
  });
  if (!response.ok) {
    throw await readError(response, 'Unable to search the curriculum.');
  }
  return response.json();
}

export async function listTopicsBySubject(
  subject: string,
  signal?: AbortSignal,
): Promise<CurriculumTopic[]> {
  const params = new URLSearchParams({ subject, limit: '100' });
  const response = await fetch(`${API_BASE_URL}/learning/topics?${params}`, {
    headers: authHeaders(),
    signal,
  });
  if (!response.ok) {
    throw await readError(response, 'Unable to load topics.');
  }
  return response.json();
}

export async function getLibraryHome(signal?: AbortSignal): Promise<LibraryHome> {
  const response = await fetch(`${API_BASE_URL}/learning/library`, {
    headers: authHeaders(),
    signal,
  });
  if (!response.ok) {
    throw await readError(response, 'Unable to load Learning Center.');
  }
  return response.json();
}

export async function toggleLearningBookmark(curriculumId: string): Promise<{
  curriculum_id: string;
  bookmarked: boolean;
  bookmarks: CurriculumTopic[];
}> {
  const response = await fetch(
    `${API_BASE_URL}/learning/bookmarks/${encodeURIComponent(curriculumId)}/toggle`,
    { method: 'POST', headers: authHeaders() },
  );
  if (!response.ok) {
    throw await readError(response, 'Could not update bookmark.');
  }
  return response.json();
}

export async function getRelatedTopics(
  curriculumId: string,
  signal?: AbortSignal,
): Promise<CurriculumTopic[]> {
  const response = await fetch(
    `${API_BASE_URL}/learning/lessons/${encodeURIComponent(curriculumId)}/related`,
    { headers: authHeaders(), signal },
  );
  if (!response.ok) {
    throw await readError(response, 'Unable to load related topics.');
  }
  const body: { topics: CurriculumTopic[] } = await response.json();
  return body.topics;
}

export async function getAITaughtLesson(
  curriculumId: string,
  signal?: AbortSignal,
): Promise<TaughtLessonResponse> {
  const response = await fetch(
    `${API_BASE_URL}/learning/lessons/${encodeURIComponent(curriculumId)}/teach`,
    {
      method: 'POST',
      headers: authHeaders(),
      signal,
    },
  );
  if (!response.ok) {
    throw await readError(response, 'Atlas AI could not prepare this lesson.');
  }
  return response.json();
}

export async function askCurriculumTutor(
  curriculumId: string,
  message: string,
  history: TutorMessage[],
): Promise<string> {
  const response = await fetch(
    `${API_BASE_URL}/learning/lessons/${encodeURIComponent(curriculumId)}/ask`,
    {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ message, history }),
    },
  );
  if (!response.ok) {
    throw await readError(response, 'Atlas AI could not answer right now.');
  }
  const body: { response: string } = await response.json();
  return body.response;
}

export async function completeCurriculumLesson(curriculumId: string): Promise<{
  xp_earned: number;
  user_xp: number;
  rank: string;
  already_completed: boolean;
}> {
  const response = await fetch(
    `${API_BASE_URL}/learning/lessons/${encodeURIComponent(curriculumId)}/complete`,
    {
      method: 'POST',
      headers: authHeaders(),
    },
  );
  if (!response.ok) {
    throw await readError(response, 'Could not save lesson completion.');
  }
  return response.json();
}
