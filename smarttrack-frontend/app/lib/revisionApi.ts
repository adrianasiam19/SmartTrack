/**
 * revisionApi.ts
 * ──────────────
 * API client for the WASSCE Revision Hub.
 * Communicates with the backend DeepSeek-powered WASSCE revision endpoints.
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

export interface TopicContent {
  title: string;
  subject: string;
  explanation: string;
  key_concepts: string[];
  formulae: { title: string; formula: string }[];
  worked_examples: { question: string; solution: string }[];
  common_mistakes: string[];
  exam_tips: string[];
  practice_questions: {
    question: string;
    options: string[];
    correct_answer: string;
    explanation: string;
  }[];
  summary: string;
  _source?: string;
}

export interface GenerateTopicResponse {
  success: boolean;
  data?: TopicContent;
  error?: string;
  source?: string;
}

export interface AskAIResponse {
  success: boolean;
  response?: string;
  error?: string;
}

/**
 * Generate WASSCE revision content for a topic via AI.
 */
export async function generateTopicContent(topic: string): Promise<GenerateTopicResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/revision/generate-topic`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ topic }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        error: errorData.detail || `Server error: ${response.status}`,
      };
    }

    return await response.json();
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : 'Failed to connect to server',
    };
  }
}

/**
 * Ask the AI a follow-up question about a revision topic.
 */
export async function askAIQuestion(
  topic: string,
  question: string,
  history?: { role: string; content: string }[]
): Promise<AskAIResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/revision/ask`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ topic, question, history }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        error: errorData.detail || `Server error: ${response.status}`,
      };
    }

    return await response.json();
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : 'Failed to connect to server',
    };
  }
}
