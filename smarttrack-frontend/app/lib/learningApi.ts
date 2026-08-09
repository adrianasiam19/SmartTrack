import { fetchWithAuth } from './authApi';

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
  /** Learner-facing visual only — no attribution / source / license. */
  visual_aid?: {
    url?: string;
    alt?: string;
    concept?: string;
    requires_labels?: boolean;
    legend?: string;
  } | null;
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
  const response = await fetchWithAuth(`${API_BASE_URL}/learning/search?${params}`, {
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
  const params = new URLSearchParams({ subject, limit: '200' });
  const response = await fetchWithAuth(`${API_BASE_URL}/learning/topics?${params}`, {
    signal,
  });
  if (!response.ok) {
    throw await readError(response, 'Unable to load topics.');
  }
  return response.json();
}

export async function exploreCurriculumTopic(
  query: string,
  subject?: string,
): Promise<CurriculumTopic> {
  const response = await fetchWithAuth(`${API_BASE_URL}/learning/explore`, {
    method: 'POST',
    body: JSON.stringify({
      query,
      ...(subject ? { subject } : {}),
    }),
  });
  if (!response.ok) {
    throw await readError(response, 'Atlas AI could not prepare this topic.');
  }
  return response.json();
}

export async function getLibraryHome(signal?: AbortSignal): Promise<LibraryHome> {
  const response = await fetchWithAuth(`${API_BASE_URL}/learning/library`, {
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
  const response = await fetchWithAuth(
    `${API_BASE_URL}/learning/bookmarks/${encodeURIComponent(curriculumId)}/toggle`,
    { method: 'POST' },
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
  const response = await fetchWithAuth(
    `${API_BASE_URL}/learning/lessons/${encodeURIComponent(curriculumId)}/related`,
    { signal },
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
  const response = await fetchWithAuth(
    `${API_BASE_URL}/learning/lessons/${encodeURIComponent(curriculumId)}/teach`,
    {
      method: 'POST',
      signal,
    },
  );
  if (!response.ok) {
    throw await readError(response, 'Atlas AI could not prepare this lesson.');
  }
  return response.json();
}

export type LearningResourceKind =
  | 'video'
  | 'pdf'
  | 'simulation'
  | 'animation'
  | 'link';

export interface LearningResource {
  id: string;
  kind: LearningResourceKind;
  title: string;
  url: string;
  provider: string;
  thumbnail_url?: string | null;
  channel?: string | null;
  duration_seconds?: number | null;
  description?: string | null;
  query?: string | null;
  extra?: {
    duration_label?: string | null;
    [key: string]: unknown;
  } | null;
}

export interface LessonResourcesResponse {
  curriculum_id: string;
  queries: string[];
  resources: LearningResource[];
}

/** Deferred optional resources (videos first). Does not block lesson teach. */
export async function getLessonResources(
  curriculumId: string,
  options?: { kinds?: LearningResourceKind[]; limit?: number; signal?: AbortSignal },
): Promise<LessonResourcesResponse> {
  const params = new URLSearchParams({
    kinds: (options?.kinds ?? ['video']).join(','),
    limit: String(options?.limit ?? 3),
  });
  const response = await fetchWithAuth(
    `${API_BASE_URL}/learning/lessons/${encodeURIComponent(curriculumId)}/resources?${params}`,
    { signal: options?.signal },
  );
  if (!response.ok) {
    throw await readError(response, 'Unable to load learning resources.');
  }
  return response.json();
}

export async function askCurriculumTutor(
  curriculumId: string,
  message: string,
  history: TutorMessage[],
): Promise<string> {
  const response = await fetchWithAuth(
    `${API_BASE_URL}/learning/lessons/${encodeURIComponent(curriculumId)}/ask`,
    {
      method: 'POST',
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
  const response = await fetchWithAuth(
    `${API_BASE_URL}/learning/lessons/${encodeURIComponent(curriculumId)}/complete`,
    {
      method: 'POST',
    },
  );
  if (!response.ok) {
    throw await readError(response, 'Could not save lesson completion.');
  }
  return response.json();
}
