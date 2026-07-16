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


def _get_fallback_psych_questions(count: int) -> list:
    """Return hardcoded fallback psychometric questions when AI/DB fails."""
    fallback = [
        {
            "id": "psych_fb_1",
            "type": "psychometric",
            "category": "Learning Style",
            "question": "When studying a new topic, what helps you understand it best?",
            "options": [
                {"value": "A", "label": "Reading notes and textbooks"},
                {"value": "B", "label": "Watching videos and diagrams"},
                {"value": "C", "label": "Discussing with friends"},
                {"value": "D", "label": "Practicing with examples"},
            ],
            "display": "choose",
        },
        {
            "id": "psych_fb_2",
            "type": "psychometric",
            "category": "Interest",
            "question": "Which school subject do you enjoy the most?",
            "options": [
                {"value": "A", "label": "Mathematics — solving problems"},
                {"value": "B", "label": "Science — discovering how things work"},
                {"value": "C", "label": "English — reading and writing"},
                {"value": "D", "label": "Social Studies — understanding the world"},
            ],
            "display": "choose",
        },
        {
            "id": "psych_fb_3",
            "type": "psychometric",
            "category": "Personality",
            "question": "How do you prefer to work on projects?",
            "options": [
                {"value": "A", "label": "Alone, at my own pace"},
                {"value": "B", "label": "In a small group, sharing ideas"},
                {"value": "C", "label": "With a partner I trust"},
                {"value": "D", "label": "Leading the team"},
            ],
            "display": "choose",
        },
        {
            "id": "psych_fb_4",
            "type": "psychometric",
            "category": "Thinking Style",
            "question": "When faced with a difficult problem, what do you usually do?",
            "options": [
                {"value": "A", "label": "Break it down step by step"},
                {"value": "B", "label": "Think of creative solutions"},
                {"value": "C", "label": "Ask someone for help"},
                {"value": "D", "label": "Keep trying different approaches"},
            ],
            "display": "choose",
        },
        {
            "id": "psych_fb_5",
            "type": "psychometric",
            "category": "Motivation",
            "question": "What motivates you most in your studies?",
            "options": [
                {"value": "A", "label": "Getting good grades"},
                {"value": "B", "label": "Learning new things"},
                {"value": "C", "label": "Making my family proud"},
                {"value": "D", "label": "Preparing for my future career"},
            ],
            "display": "choose",
        },
        {
            "id": "psych_fb_6",
            "type": "psychometric",
            "category": "Study Habit",
            "question": "When do you study most effectively?",
            "options": [
                {"value": "A", "label": "Early morning, when it's quiet"},
                {"value": "B", "label": "Afternoon, after school"},
                {"value": "C", "label": "Evening, before bed"},
                {"value": "D", "label": "In short bursts throughout the day"},
            ],
            "display": "choose",
        },
        {
            "id": "psych_fb_7",
            "type": "psychometric",
            "category": "Collaboration",
            "question": "In a group discussion, you usually:",
            "options": [
                {"value": "A", "label": "Listen first, then share your thoughts"},
                {"value": "B", "label": "Lead the conversation"},
                {"value": "C", "label": "Take notes and organize ideas"},
                {"value": "D", "label": "Encourage others to speak"},
            ],
            "display": "choose",
        },
        {
            "id": "psych_fb_8",
            "type": "psychometric",
            "category": "Interest",
            "question": "What kind of career interests you most?",
            "options": [
                {"value": "A", "label": "Science and technology"},
                {"value": "B", "label": "Arts and creativity"},
                {"value": "C", "label": "Business and leadership"},
                {"value": "D", "label": "Healthcare and helping others"},
            ],
            "display": "choose",
        },
    ]
    random.shuffle(fallback)
    return fallback[:count]


def _get_fallback_academic_questions(count: int, shs_level: str) -> list:
    """Return hardcoded fallback academic diagnostic questions when AI fails."""
    fallback = [
        {
            "id": "acad_fb_1",
            "type": "academic",
            "domain": "Core Mathematics",
            "question": "What is 25% of 200?",
            "options": {"A": "25", "B": "50", "C": "75", "D": "100"},
            "correct_key": "B",
            "explanation": "25% means 25/100 = 0.25. So 0.25 x 200 = 50.",
        },
        {
            "id": "acad_fb_2",
            "type": "academic",
            "domain": "English Language",
            "question": "Which of the following is a complete sentence?",
            "options": {"A": "Running quickly.", "B": "The boy runs.", "C": "Under the table.", "D": "Beautiful flowers."},
            "correct_key": "B",
            "explanation": "'The boy runs' has both a subject (the boy) and a verb (runs), making it a complete sentence.",
        },
        {
            "id": "acad_fb_3",
            "type": "academic",
            "domain": "Integrated Science",
            "question": "Which organ in the human body pumps blood?",
            "options": {"A": "Lungs", "B": "Liver", "C": "Heart", "D": "Kidneys"},
            "correct_key": "C",
            "explanation": "The heart is a muscular organ that pumps blood throughout the body via the circulatory system.",
        },
        {
            "id": "acad_fb_4",
            "type": "academic",
            "domain": "Logical Reasoning",
            "question": "If all birds can fly, and a penguin is a bird, can a penguin fly?",
            "options": {"A": "Yes, because all birds fly", "B": "No, because penguins cannot fly", "C": "Only if it's young", "D": "Penguins are not birds"},
            "correct_key": "B",
            "explanation": "While all birds share common characteristics, not all birds can fly. Penguins are birds but they are flightless.",
        },
        {
            "id": "acad_fb_5",
            "type": "academic",
            "domain": "Social Studies",
            "question": "What is the capital city of Ghana?",
            "options": {"A": "Kumasi", "B": "Accra", "C": "Takoradi", "D": "Tamale"},
            "correct_key": "B",
            "explanation": "Accra is the capital and largest city of Ghana, located along the Atlantic coast.",
        },
        {
            "id": "acad_fb_6",
            "type": "academic",
            "domain": "Analytical Thinking",
            "question": "A shirt costs GHS 80 and is on sale for 20% off. What is the sale price?",
            "options": {"A": "GHS 60", "B": "GHS 64", "C": "GHS 72", "D": "GHS 16"},
            "correct_key": "B",
            "explanation": "20% of 80 = 16. So the sale price is 80 - 16 = GHS 64.",
        },
        {
            "id": "acad_fb_7",
            "type": "academic",
            "domain": "Core Mathematics",
            "question": "Solve for x: 2x + 5 = 15",
            "options": {"A": "x = 5", "B": "x = 10", "C": "x = 7.5", "D": "x = 20"},
            "correct_key": "A",
            "explanation": "2x + 5 = 15. Subtract 5 from both sides: 2x = 10. Divide by 2: x = 5.",
        },
        {
            "id": "acad_fb_8",
            "type": "academic",
            "domain": "English Language",
            "question": "Choose the correct spelling:",
            "options": {"A": "Acommodate", "B": "Accommodate", "C": "Acomodate", "D": "Accomodate"},
            "correct_key": "B",
            "explanation": "The correct spelling is 'accommodate' with double 'c' and double 'm'.",
        },
        {
            "id": "acad_fb_9",
            "type": "academic",
            "domain": "Integrated Science",
            "question": "What gas do plants absorb from the atmosphere during photosynthesis?",
            "options": {"A": "Oxygen", "B": "Nitrogen", "C": "Carbon dioxide", "D": "Hydrogen"},
            "correct_key": "C",
            "explanation": "Plants absorb carbon dioxide (CO2) from the atmosphere and use it with sunlight to produce glucose and oxygen.",
        },
        {
            "id": "acad_fb_10",
            "type": "academic",
            "domain": "Logical Reasoning",
            "question": "All squares are rectangles. Some rectangles are not squares. Therefore:",
            "options": {"A": "Some squares are not rectangles", "B": "All rectangles are squares", "C": "Some rectangles are squares", "D": "No squares are rectangles"},
            "correct_key": "C",
            "explanation": "All squares are rectangles by definition, so some rectangles (the ones that have equal sides) are squares.",
        },
    ]
    random.shuffle(fallback)
    return fallback[:count]


async def generate_starter_session(
    db: AsyncSession,
    user_id: str,
    shs_level: str = "SHS 1",
    programme: str = "General Science",
    psychometric_count: int = 6,
    academic_count: int = 6,
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

    # If not enough from DB → try AI generation (avoids repeats from both DB + fallback)
    if len(psych_questions) < psychometric_count:
        needed = psychometric_count - len(psych_questions)
        logger.info(f"Not enough DB psychometric cards, generating {needed} via AI...")

        # Build list of existing questions so AI knows what to avoid
        all_existing_texts = set()
        for c in db_psych_cards:
            all_existing_texts.add(c.question)
        for q in psych_questions:
            all_existing_texts.add(q["question"])
        # Add hardcoded fallback questions to avoid AI generating duplicates of those
        for fb in _get_fallback_psych_questions(100):  # Get all (capped at 8)
            all_existing_texts.add(fb["question"])
        existing_text = "\n".join(f"- {q}" for q in sorted(all_existing_texts))

        ai_psych = await _generate_psychometric_questions(
            count=needed,
            existing_questions=existing_text,
        )
        # Filter out any AI-generated questions that still match DB ones
        if ai_psych:
            seen_questions = {q["question"] for q in psych_questions}
            seen_questions.update(c.question for c in db_psych_cards)
            for gen_q in ai_psych:
                if gen_q["question"] not in seen_questions:
                    psych_questions.append(gen_q)
                    seen_questions.add(gen_q["question"])

    # If STILL not enough → use hardcoded fallback as last resort
    if len(psych_questions) < psychometric_count:
        needed = psychometric_count - len(psych_questions)
        logger.info(f"AI generation also failed, using hardcoded fallback for {needed} questions")
        seen_questions = {q["question"] for q in psych_questions}
        for fb_q in _get_fallback_psych_questions(needed):
            if fb_q["question"] not in seen_questions:
                psych_questions.append(fb_q)
                seen_questions.add(fb_q["question"])

    # ── 2. Generate academic diagnostic questions via AI ───────────────────
    # Try AI first (level-adapted), fall back to hardcoded if AI fails
    academic_questions = await _generate_academic_questions(
        count=academic_count,
        shs_level=shs_level,
    )
    if not academic_questions:
        logger.info("AI academic generation failed, using hardcoded fallback")
        academic_questions = _get_fallback_academic_questions(
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
    Generate a learner profile from Starter Arena responses.

    Uses a quick fallback profile instantly — no slow AI call at the end.
    The responses are stored locally and can be analyzed deeper later.
    """
    # Instant: use fallback profile based on response analysis
    # This avoids the long "loading insight" wait
    return _quick_learner_profile(
        shs_level=shs_level,
        programme=programme,
        psychometric_responses=psychometric_responses,
        academic_responses=academic_responses,
    )


def _quick_learner_profile(
    shs_level: str,
    programme: str,
    psychometric_responses: list,
    academic_responses: list,
) -> dict:
    """Build a learner profile instantly from response data (no AI call)."""
    # Calculate accuracy from academic responses
    academic_correct = sum(1 for r in academic_responses if r.get("correct"))
    academic_total = len(academic_responses)
    accuracy = (academic_correct / academic_total * 100) if academic_total > 0 else 0

    # Estimate confidence from response times
    avg_time = 0
    if academic_responses:
        times = [r.get("time_taken", 0) for r in academic_responses]
        avg_time = sum(times) / len(times) if times else 0

    # Build profile based on actual data
    strengths = []
    weaknesses = []
    recommended_challenges = []

    if accuracy >= 70:
        strengths.append("Strong academic foundation")
        recommended_challenges.append("Competitive Challenges")
    elif accuracy >= 50:
        strengths.append("Good understanding of core concepts")
        weaknesses.append("Could benefit from more practice")
        recommended_challenges.append("Logic Arena")
    else:
        weaknesses.append("Core concepts need reinforcement")
        recommended_challenges.append("Learning Center")

    if avg_time < 15 and accuracy >= 60:
        strengths.append("Quick thinking and good recall")
    elif avg_time >= 15:
        weaknesses.append("Could improve problem-solving speed")
        recommended_challenges.append("Quantitative Sprint")

    # Learning style from psychometric data
    learning_style = "Visual"  # Default
    for r in psychometric_responses:
        q = r.get("question", "").lower()
        a = r.get("answer", "")
        if "study" in q or "learn" in q:
            if a == "A":
                learning_style = "Reading"
            elif a == "B":
                learning_style = "Visual"
            elif a == "C":
                learning_style = "Auditory"
            elif a == "D":
                learning_style = "Kinesthetic"
            break

    confidence = "High" if accuracy >= 70 else "Medium" if accuracy >= 40 else "Low"
    reasoning = "High" if accuracy >= 75 else "Medium" if accuracy >= 45 else "Low"

    return {
        "learning_style": {
            "primary": learning_style,
            "description": f"Your responses suggest a {learning_style.lower()} learning preference. Atlas will tailor content to match your style."
        },
        "academic_strengths": strengths + [f"Programme: {programme}"],
        "academic_weaknesses": weaknesses or ["Areas to explore further"],
        "confidence_level": confidence,
        "reasoning_ability": reasoning,
        "recommended_focus": f"Based on your Starter Arena results, focus on {weaknesses[0].lower() if weaknesses else 'strengthening your core subjects'} to build a strong foundation for {shs_level}.",
        "recommended_challenges": recommended_challenges + ["Daily Challenges"],
        "recommendation_profile": f"SHS {shs_level} student in {programme}. Accuracy: {accuracy:.0f}%, Confidence: {confidence}, Style: {learning_style}."
    }


