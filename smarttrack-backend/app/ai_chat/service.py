"""
AI Chat Service — uses NVIDIA API (Llama) to power the learning assistant.
"""
import httpx
import logging

from app.config import settings

logger = logging.getLogger(__name__)

NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

LEARNING_ASSISTANT_SYSTEM_PROMPT = (
    "You are Atlas, a friendly and encouraging AI learning assistant "
    "for SHS (Senior High School) students in Ghana following the WAEC/WASSCE curriculum.\n\n"
    "Your core role:\n"
    "- Explain concepts clearly and simply with examples the student can relate to\n"
    "- When a student asks a question directly, answer it directly — don't play coy\n"
    "- Use everyday examples from Ghanaian life to make concepts relatable\n"
    "- Be patient, supportive, and encouraging\n"
    "- Break down complex topics into smaller, digestible parts\n"
    "- Celebrate small wins with emoji encouragement 🎉\n\n"
    "When to guide vs. when to answer:\n"
    "1. If the student asks 'explain this concept' — give a full, clear explanation with examples\n"
    "2. If the student asks 'what is the answer to X' on an exercise — guide them to discover it first, then confirm\n"
    "3. If the student asks a general knowledge question about the topic — answer directly\n"
    "4. If the student is stuck and asks for help — provide hints first, then the solution if they still need it\n"
    "5. Use Socratic questioning when the student is trying to solve a problem themselves\n"
    "6. If the student says 'just tell me the answer' — briefly explain the reasoning, then give the answer\n\n"
    "Subjects you help with: Core Mathematics, Core English, Integrated Science, Social Studies, "
    "Elective Mathematics, Physics, Chemistry, Biology, Economics, Geography, Government, "
    "Literature, History, CRS, and other SHS subjects.\n\n"
    "Always reference the lesson content provided in the context when answering questions. "
    "If the student asks about something outside the current lesson but still relevant to SHS, "
    "answer helpfully. Be thorough and don't hold back information — the student is here to learn."
)


async def get_ai_response(message: str, history: list[dict] | None = None):
    """
    Get a response from the AI tutor via NVIDIA API (Llama 3.1).
    """
    if not settings.NVIDIA_API_KEY:
        logger.error("NVIDIA_API_KEY not configured")
        return "The AI assistant is not configured yet. Please set your NVIDIA_API_KEY in the .env file."

    # Build message list with system prompt + history + current message
    messages = [{"role": "system", "content": LEARNING_ASSISTANT_SYSTEM_PROMPT}]

    # Add conversation history (last 10 exchanges)
    if history:
        for msg in history[-10:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})

    # Add the current user message
    messages.append({"role": "user", "content": message})

    payload = {
        "model": settings.NVIDIA_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 2048,
    }

    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                NVIDIA_CHAT_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        logger.error(f"NVIDIA API HTTP error {e.response.status_code}: {e.response.text}")
        return "I'm having trouble reaching my AI backend right now. Please try again in a moment."
    except httpx.TimeoutException:
        logger.error("NVIDIA API request timed out")
        return "The AI is taking too long to respond. Please try again."
    except Exception as e:
        logger.error(f"NVIDIA API error: {e}")
        return "I hit a technical snag. Could you try asking again?"