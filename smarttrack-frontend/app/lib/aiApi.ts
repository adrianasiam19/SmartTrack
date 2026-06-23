/**
 * aiApi.ts
 * ─────────
 * AI Learning Assistant API client.
 * Communicates with the backend Gemini-powered chat endpoint.
 */

const API_BASE_URL =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) ||
  'http://localhost:8000/api/v1';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history?: { role: string; content: string }[];
  lesson_context?: string;
}

export interface ChatResponse {
  response: string;
}

const getAuthHeaders = (): HeadersInit => {
  if (typeof window === 'undefined') return { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('accessToken');
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

/**
 * Send a message to the AI learning assistant and get a response.
 */
export async function sendChatMessage(
  message: string,
  history?: ChatMessage[],
  lessonContext?: string
): Promise<string> {
  const formattedHistory = history?.map((msg) => ({
    role: msg.role,
    content: msg.content,
  }));

  const response = await fetch(`${API_BASE_URL}/ai/chat`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      message,
      history: formattedHistory,
      lesson_context: lessonContext,
    } as ChatRequest),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to get AI response');
  }

  const data: ChatResponse = await response.json();
  return data.response;
}

/**
 * Get a hint for a specific question/topic.
 * This is a convenience wrapper around sendChatMessage.
 */
export async function getHint(
  question: string,
  lessonContext: string
): Promise<string> {
  return sendChatMessage(
    `Can you give me a hint for this question without giving away the answer?\n\n${question}`,
    undefined,
    lessonContext
  );
}

/**
 * Get an explanation for a concept.
 */
export async function getExplanation(
  concept: string,
  lessonContext: string
): Promise<string> {
  return sendChatMessage(
    `Can you explain "${concept}" in a simple way with an example?`,
    undefined,
    lessonContext
  );
}
