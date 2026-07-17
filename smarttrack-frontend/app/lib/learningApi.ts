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

function authHeaders(): HeadersInit {
  const token = getAccessToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function readError(response: Response, fallback: string): Promise<Error> {
  const body = await response.json().catch(() => null);
  return new Error(body?.detail || fallback);
}

export async function searchCurriculumTopics(
  query: string,
  signal?: AbortSignal,
): Promise<CurriculumTopic[]> {
  const params = new URLSearchParams({ query, limit: '20' });
  const response = await fetch(`${API_BASE_URL}/learning/topics?${params}`, {
    headers: authHeaders(),
    signal,
  });
  if (!response.ok) {
    throw await readError(response, 'Unable to search your curriculum.');
  }
  return response.json();
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
