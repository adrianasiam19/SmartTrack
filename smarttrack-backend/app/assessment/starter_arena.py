"""
starter_arena.py — Adaptive Starter Arena for onboarding

Generates a mixed session of psychometric and academic diagnostic questions.
Psychometric questions come from the database (with AI fallback).
Academic questions are generated via AI, adapted to the student's SHS level.
"""
import json
import logging
import random
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.assessment.models import PsychometricCard, PsychometricResponse

logger = logging.getLogger(__name__)

DEEPSEEK_CHAT_URL = "https://api.deepseek.com/v1/chat/completions"
NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

STARTER_SYSTEM_PROMPT = (
    "You are Atlas, an intelligent onboarding assistant for SHS students in Ghana. "
    "Your role is to help Atlas understand the student's learning style, academic readiness, "
    "and interests through a friendly, conversational onboarding experience.\n\n"
    "Generate questions that are:\n"
    "- Short and engaging (not exam-like)\n"
    "- Conversational and friendly in tone\n"
    "- Appropriate for the student's SHS level\n"
    "- Designed to reveal the student's thinking process, not just right/wrong answers\n\n"
    "Subjects: Core Mathematics, English Language, Integrated Science, Social Studies, "
    "Logical reasoning, Analytical thinking"
)

# ── Academic diagnostic question templates per SHS level ────────────────────
ACADEMIC_PROMPTS = {
    "SHS 1": (
        "Generate {count} short academic diagnostic questions for an SHS 1 student in Ghana. "
        "Mix questions across: Core Mathematics, English Language, Integrated Science, Social Studies, "
        "Logical reasoning, Analytical thinking.\n\n"
        "Each question should test understanding of SHS 1-level concepts. "
        "Make them conversational, not exam-like. "
        "Keep each question very short (1-2 sentences max).\n\n"
        "Return ONLY valid JSON array (no markdown) with this structure:\n"
        "[\n"
        '  {{\n'
        '    "id": "acad_1",\n'
        '    "type": "academic",\n'
        '    "domain": "Core Mathematics",\n'
        '    "question": "Short question text",\n'
        '    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},\n'
        '    "correct_key": "A",\n'
        '    "explanation": "Brief friendly explanation"\n'
        '  }}\n'
        "]"
    ),
    "SHS 2": (
        "Generate {count} short academic diagnostic questions for an SHS 2 student in Ghana. "
        "Mix questions across: Core Mathematics, English Language, Integrated Science, Social Studies, "
        "Logical reasoning, Analytical thinking.\n\n"
        "Each question should test understanding of SHS 2-level concepts. "
        "Include slightly more complex reasoning than SHS 1. "
        "Keep each question short (1-2 sentences max).\n\n"
        "Return ONLY valid JSON array (no markdown) with this structure:\n"
        "[\n"
        '  {{\n'
        '    "id": "acad_1",\n'
        '    "type": "academic",\n'
        '    "domain": "Core Mathematics",\n'
        '    "question": "Short question text",\n'
        '    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},\n'
        '    "correct_key": "A",\n'
        '    "explanation": "Brief friendly explanation"\n'
        '  }}\n'
        "]"
    ),
    "SHS 3": (
        "Generate {count} WASSCE-level diagnostic questions for an SHS 3 student in Ghana. "
        "Mix questions across: Core Mathematics, English Language, Integrated Science, Social Studies, "
        "Logical reasoning, Analytical thinking.\n\n"
        "Each question should test WASSCE-level understanding. "
        "Include questions that require critical thinking and application of concepts. "
        "Keep each question short and focused.\n\n"
        "Return ONLY valid JSON array (no markdown) with this structure:\n"
        "[\n"
        '  {{\n'
        '    "id": "acad_1",\n'
        '    "type": "academic",\n'
        '    "domain": "Core Mathematics",\n'
        '    "question": "Short question text",\n'
        '    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},\n'
        '    "correct_key": "A",\n'
        '    "explanation": "Brief friendly explanation"\n'
        '  }}\n'
        "]"
    ),
}

# ── Psychometric generation prompt (used only when DB runs low) ────────────
PSYCHOMETRIC_GENERATION_PROMPT = (
    "Generate {count} unique psychometric/interest discovery questions for an SHS student in Ghana. "
    "These questions help understand the student's learning style, interests, personality, "
    "and preferences — NOT their academic knowledge.\n\n"
    "Make questions:\n"
    "- Conversational and natural\n"
    "- About learning preferences, interests, study habits, personality\n"
    "- Culturally relevant to Ghanaian SHS students\n"
    "- With 4 balanced options (A, B, C, D) that reveal different traits\n\n"
    "Avoid generating questions similar to these existing ones (check for duplicates):\n"
    "{existing_questions}\n\n"
    "Return ONLY valid JSON array (no markdown) with this structure:\n"
    "[\n"
    '  {{\n'
    '    "id": "psych_gen_1",\n'
    '    "type": "psychometric",\n'
    '    "category": "Learning Style",\n'
    '    "question": "Natural conversational question?",\n'
    '    "options": [\n'
    '      {{"value": "A", "label": "First option"}},\n'
    '      {{"value": "B", "label": "Second option"}},\n'
    '      {{"value": "C", "label": "Third option"}},\n'
    '      {{"value": "D", "label": "Fourth option"}}\n'
    '    ]\n'
    '  }}\n'
    "]"
)

# ── Learner profile generation prompt ──────────────────────────────────────
LEARNER_PROFILE_PROMPT = (
    "You are Atlas, an intelligent learning analyst. Based on a student's responses to "
    "a Starter Arena session, generate a detailed learner profile.\n\n"
    "The session contained:\n"
    "- Psychometric questions (learning style, interests, preferences)\n"
    "- Academic diagnostic questions (knowledge across subjects)\n\n"
    "Student info:\n"
    "- SHS Level: {shs_level}\n"
    "- Programme: {programme}\n\n"
    "Psychometric responses:\n"
    "{psychometric_responses}\n\n"
    "Academic responses:\n"
    "{academic_responses}\n\n"
    "Return ONLY valid JSON (no markdown) with this structure:\n"
    "{{\n"
    '  "learning_style": {{\n'
    '    "primary": "Visual/Auditory/Kinesthetic/Reading",\n'
    '    "description": "2-3 sentence description"\n'
    '  }},\n'
    '  "academic_strengths": ["Strength 1", "Strength 2"],\n'
    '  "academic_weaknesses": ["Weakness 1", "Weakness 2"],\n'
    '  "confidence_level": "Low/Medium/High",\n'
    '  "reasoning_ability": "Low/Medium/High",\n'
    '  "recommended_focus": "2-3 sentence recommendation",\n'
    '  "recommended_challenges": ["Challenge area 1", "Challenge area 2"],\n'
    '  "recommendation_profile": "Brief summary for the recommendation engine"\n'
    "}}"
)


async def get_ai_response(messages: list, model: str = "") -> str:
    """Send messages to AI and return the response text."""
    providers = []
    if settings.DEEPSEEK_API_KEY:
        providers.append({
            "name": "DeepSeek",
            "url": DEEPSEEK_CHAT_URL,
            "model": settings.DEEPSEEK_MODEL,
            "api_key": settings.DEEPSEEK_API_KEY,
        })
    if settings.NVIDIA_API_KEY:
        providers.append({
            "name": "NVIDIA",
            "url": NVIDIA_CHAT_URL,
            "model": settings.NVIDIA_MODEL,
            "api_key": settings.NVIDIA_API_KEY,
        })

    for provider in providers:
        try:
            headers = {
                "Authorization": f"Bearer {provider['api_key']}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": provider["model"],
                "messages": messages,
                "temperature": 0.6,
                "max_tokens": 4096,
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(provider["url"], headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"{provider['name']} failed: {e}")
            continue
    return ""


async def generate_starter_session(
    db: AsyncSession,
    user_id: str,
    shs_level: str = "SHS 1",
    programme: str = "General Science",
    psychometric_count: int = 5,
    academic_count: int = 5,
) -> dict:
    """
    Generate a complete Starter Arena session with mixed questions.

    Returns:
        dict with:
          - session_id: str
          - questions: list of question dicts (alternating psychometric + academic)
          - total_count: int
    """
    session_id = f"sa_{user_id}_{random.randint(10000, 99999)}"
    questions = []

    # ── 1. Fetch psychometric questions from database ─────────────────────
    db_psych_cards = []
    try:
        result = await db.execute(
            select(PsychometricCard).order_by(PsychometricCard.card_id)
        )
        db_psych_cards = result.scalars().all()
    except Exception as e:
        logger.warning(f"Failed to fetch psychometric cards from DB: {e}")

    # Get already-seen card IDs for this user
    seen_card_ids = set()
    try:
        seen_result = await db.execute(
            select(PsychometricResponse.card_id).where(
                PsychometricResponse.user_id == user_id
            )
        )
        seen_card_ids = {row[0] for row in seen_result.fetchall()}
    except Exception:
        pass

    # Filter out seen cards
    available_cards = [c for c in db_psych_cards if c.card_id not in seen_card_ids]

    # Shuffle available cards
    random.shuffle(available_cards)

    # Format as standard psychometric questions
    psych_questions = []
    for card in available_cards[:psychometric_count]:
        psych_questions.append({
            "id": f"psych_{card.card_id}",
            "type": "psychometric",
            "category": card.category or "Insight",
            "question": card.question,
            "options": card.options,
            "display": "choose",
        })

    # If we don't have enough from DB, generate the rest via AI
    if len(psych_questions) < psychometric_count:
        needed = psychometric_count - len(psych_questions)
        existing_descriptions = [
            f"- {q['question']}" for q in psych_questions
        ]
        ai_psych = await _generate_psychometric_questions(
            needed, existing_questions="\n".join(existing_descriptions) or "None"
        )
        psych_questions.extend(ai_psych)

    # ── 2. Generate academic diagnostic questions via AI ──────────────────
    academic_questions = await _generate_academic_questions(
        count=academic_count,
        shs_level=shs_level,
    )

    # ── 3. Alternate questions naturally ──────────────────────────────────
    # Weave psychometric and academic questions alternately for a conversational flow
    total = max(len(psych_questions), len(academic_questions))
    for i in range(total):
        if i < len(psych_questions):
            questions.append(psych_questions[i])
        if i < len(academic_questions):
            questions.append(academic_questions[i])

    return {
        "session_id": session_id,
        "questions": questions,
        "total_count": len(questions),
    }


async def _generate_psychometric_questions(count: int, existing_questions: str = "") -> list:
    """Generate psychometric questions via AI."""
    prompt = PSYCHOMETRIC_GENERATION_PROMPT.format(
        count=count,
        existing_questions=existing_questions,
    )
    response = await get_ai_response([
        {"role": "system", "content": STARTER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])
    if not response:
        return []

    try:
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return json.loads(response)
    except Exception as e:
        logger.error(f"Failed to parse AI psychometric questions: {e}")
        return []


async def _generate_academic_questions(count: int, shs_level: str) -> list:
    """Generate academic diagnostic questions adapted to SHS level."""
    prompt_template = ACADEMIC_PROMPTS.get(shs_level, ACADEMIC_PROMPTS["SHS 1"])
    prompt = prompt_template.format(count=count)

    response = await get_ai_response([
        {"role": "system", "content": STARTER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])
    if not response:
        return []

    try:
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return json.loads(response)
    except Exception as e:
        logger.error(f"Failed to parse academic questions: {e}")
        return []


async def generate_learner_profile(
    shs_level: str,
    programme: str,
    psychometric_responses: list,
    academic_responses: list,
) -> dict:
    """
    Generate a detailed learner profile after the Starter Arena is complete.

    Returns a dict with the learner profile structure.
    """
    prompt = LEARNER_PROFILE_PROMPT.format(
        shs_level=shs_level,
        programme=programme,
        psychometric_responses=json.dumps(psychometric_responses, indent=2),
        academic_responses=json.dumps(academic_responses, indent=2),
    )

    response = await get_ai_response([
        {"role": "system", "content": STARTER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    if not response:
        return _fallback_learner_profile(shs_level, programme)

    try:
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return json.loads(response)
    except Exception as e:
        logger.error(f"Failed to parse learner profile: {e}")
        return _fallback_learner_profile(shs_level, programme)


def _fallback_learner_profile(shs_level: str, programme: str) -> dict:
    """Return a basic fallback learner profile."""
    return {
        "learning_style": {
            "primary": "Mixed",
            "description": "Learning style analysis will improve as you complete more activities."
        },
        "academic_strengths": ["General knowledge"],
        "academic_weaknesses": ["Areas to be identified through further assessment"],
        "confidence_level": "Medium",
        "reasoning_ability": "Medium",
        "recommended_focus": "Complete the Starter Arena to receive personalized recommendations.",
        "recommended_challenges": ["Logic Arena", "Quantitative Sprint"],
        "recommendation_profile": "Profile generation in progress. Complete more challenges for better insights."
    }
