"""
revision/service.py — WASSCE Revision AI service

Generates comprehensive WASSCE revision content for SHS 3 students
using DeepSeek AI (with NVIDIA fallback).
"""
import json
import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

DEEPSEEK_CHAT_URL = "https://api.deepseek.com/v1/chat/completions"
NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

WASSCE_SYSTEM_PROMPT = (
    "You are Atlas, an expert WASSCE revision tutor for SHS 3 students in Ghana. "
    "You specialize in helping students revise topics across all SHS subjects: "
    "Core Mathematics, English Language, Integrated Science, Social Studies, "
    "Biology, Chemistry, Physics, Elective Mathematics, and more.\n\n"
    "When generating content, follow these principles:\n"
    "1. Be thorough but clear — use simple language SHS students understand\n"
    "2. Include real WASSCE-style examples and practice questions\n"
    "3. Highlight common mistakes students make\n"
    "4. Provide exam tips and memory aids\n"
    "5. Use Ghanaian context where appropriate\n"
    "6. Format responses in clean, structured JSON or plain text as requested\n\n"
    "Always be encouraging and supportive. WASSCE revision can be stressful — "
    "keep students motivated!"
)


async def generate_topic_content(topic: str) -> dict:
    """
    Generate comprehensive WASSCE revision content for a given topic.

    Returns a dict with:
      - title: str
      - subject: str
      - explanation: str (simple, clear explanation)
      - key_concepts: list[str]
      - formulae: list[dict] (title + formula, empty list if not applicable)
      - worked_examples: list[dict] (question + solution)
      - common_mistakes: list[str]
      - exam_tips: list[str]
      - practice_questions: list[dict] (question + options + answer + explanation)
      - summary: str
    """
    prompt = f"""Generate comprehensive WASSCE revision content for the topic: "{topic}"

The student is an SHS 3 student in Ghana preparing for WASSCE.

Return ONLY valid JSON (no markdown, no code blocks) with this exact structure:
{{
    "title": "Topic title (capitalized properly)",
    "subject": "The subject this topic belongs to (e.g., Core Mathematics, Biology, Physics, English Language, etc.)",
    "explanation": "A clear, simple explanation of the topic in 3-5 paragraphs. Use examples.",
    "key_concepts": ["Concept 1", "Concept 2", "Concept 3"],
    "formulae": [
        {{"title": "Formula name", "formula": "Formula expression"}}
    ],
    "worked_examples": [
        {{"question": "A WASSCE-style question", "solution": "Step-by-step solution"}}
    ],
    "common_mistakes": [
        "Common mistake 1 with explanation",
        "Common mistake 2 with explanation"
    ],
    "exam_tips": [
        "Tip 1 for WASSCE exam",
        "Tip 2 for WASSCE exam"
    ],
    "practice_questions": [
        {{
            "question": "Multiple choice question",
            "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
            "correct_answer": "A. Option 1",
            "explanation": "Why this answer is correct"
        }}
    ],
    "summary": "A brief 2-3 sentence summary of the topic"
}}

Rules:
- Provide 2-3 worked examples
- Provide 2-3 practice questions
- If the topic has no formulae, return an empty array for formulae
- Make the content directly relevant to the WASSCE/Ghanaian SHS curriculum
- Include real WASSCE-style question formats
"""

    logger.info(f"Generating WASSCE revision content for topic: '{topic}'")

    # Try DeepSeek first, then NVIDIA fallback
    ai_providers = []

    if settings.DEEPSEEK_API_KEY:
        ai_providers.append({
            "name": "DeepSeek",
            "url": DEEPSEEK_CHAT_URL,
            "model": settings.DEEPSEEK_MODEL,
            "api_key": settings.DEEPSEEK_API_KEY,
        })

    if settings.NVIDIA_API_KEY:
        ai_providers.append({
            "name": "NVIDIA",
            "url": NVIDIA_CHAT_URL,
            "model": settings.NVIDIA_MODEL,
            "api_key": settings.NVIDIA_API_KEY,
        })

    if not ai_providers:
        return _fallback_topic_content(topic)

    for provider in ai_providers:
        try:
            headers = {
                "Authorization": f"Bearer {provider['api_key']}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": provider["model"],
                "messages": [
                    {"role": "system", "content": WASSCE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.6,
                "top_p": 0.95,
                "max_tokens": 4096,
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    provider["url"],
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                raw = result["choices"][0]["message"]["content"]

                # Clean markdown code block wrappers if present
                raw = raw.strip()
                if raw.startswith("```json"):
                    raw = raw[7:]
                elif raw.startswith("```"):
                    raw = raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()

                data = json.loads(raw)
                data["_source"] = provider["name"]
                logger.info(f"Topic content generated via {provider['name']} for '{topic}'")
                return data

        except Exception as e:
            logger.warning(f"{provider['name']} failed for topic '{topic}': {e}")
            continue

    # All providers failed
    logger.error(f"All AI providers failed for topic '{topic}'")
    return _fallback_topic_content(topic)


def _fallback_topic_content(topic: str) -> dict:
    """Return a basic fallback when AI generation fails."""
    return {
        "title": topic,
        "subject": "General Studies",
        "explanation": (
            f"This is a key topic in the WASSCE syllabus. "
            f"Unfortunately, we could not generate detailed content right now. "
            f"Please try again, or ask the AI tutor for help with '{topic}'."
        ),
        "key_concepts": [f"Review the core principles of {topic}"],
        "formulae": [],
        "worked_examples": [],
        "common_mistakes": ["Ensure you understand the basic concepts before attempting questions."],
        "exam_tips": ["Practice past WASSCE questions on this topic to build confidence."],
        "practice_questions": [],
        "summary": f"Revise {topic} thoroughly using your textbooks and past questions.",
        "_source": "fallback",
    }


async def ask_ai_question(topic: str, question: str, history: Optional[list] = None) -> str:
    """
    Ask a follow-up question about a specific revision topic.
    Uses the existing AI chat infrastructure.
    """
    prompt = f"[Revising: {topic}]\n\n{question}"

    # Reuse the same provider logic
    ai_providers = []
    if settings.DEEPSEEK_API_KEY:
        ai_providers.append({
            "name": "DeepSeek",
            "url": DEEPSEEK_CHAT_URL,
            "model": settings.DEEPSEEK_MODEL,
            "api_key": settings.DEEPSEEK_API_KEY,
        })
    if settings.NVIDIA_API_KEY:
        ai_providers.append({
            "name": "NVIDIA",
            "url": NVIDIA_CHAT_URL,
            "model": settings.NVIDIA_MODEL,
            "api_key": settings.NVIDIA_API_KEY,
        })

    if not ai_providers:
        return "The AI assistant is not configured. Please set an API key in the .env file."

    messages = [{"role": "system", "content": WASSCE_SYSTEM_PROMPT}]
    if history:
        for msg in history[-10:]:
            role = "user" if msg.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": msg.get("content", "")})
    messages.append({"role": "user", "content": prompt})

    for provider in ai_providers:
        try:
            headers = {
                "Authorization": f"Bearer {provider['api_key']}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": provider["model"],
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    provider["url"],
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.warning(f"{provider['name']} failed for AI question: {e}")
            continue

    return "I'm sorry, I couldn't process your question right now. Please try again."
