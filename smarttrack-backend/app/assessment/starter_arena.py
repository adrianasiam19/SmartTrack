"""
starter_arena.py — Adaptive Starter Arena for onboarding

Generates a mixed session of psychometric and academic diagnostic questions.
Psychometric questions come from the database (with AI fallback).
Academic questions are generated via AI, adapted to the student's SHS level.
"""
import asyncio
import json
import logging
import random
import re
from difflib import SequenceMatcher
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.assessment.models import PsychometricCard, PsychometricResponse
from app.assessment.psychometric_cards import PSYCHOMETRIC_CARDS

logger = logging.getLogger(__name__)

# ── In-memory cache for AI-generated questions ────────────────────────────
# Stores the latest AI-generated psychometric + academic questions so they
# can be used in the NEXT Starter Arena session (avoids repeats).
_ai_question_cache = {
    "psychometric": [],  # list of question dicts
    "academic": {},      # { "SHS 1": [...], "SHS 2": [...], "SHS 3": [...] }
}

DEEPSEEK_CHAT_URL = "https://api.deepseek.com/v1/chat/completions"
NVIDIA_CHAT_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

STARTER_SYSTEM_PROMPT = (
    "You are Atlas, an intelligent onboarding partner for SHS students in Ghana. "
    "The Starter Arena is NOT an examination. Your job is to help Atlas understand how "
    "the learner thinks, learns, decides, creates, and solves problems through a warm, "
    "conversational discovery experience.\n\n"
    "Generate questions that are:\n"
    "- Short, engaging, and non-exam-like\n"
    "- Conversational and friendly in tone\n"
    "- Age-appropriate for the student's SHS level\n"
    "- Focused on thinking patterns, preferences, and judgement — never memorised facts\n"
    "- Varied in format and complementary to previously asked questions"
)

PSYCHOMETRIC_CATEGORY_PLAN = [
    "Learning Preferences",
    "Curiosity",
    "Creativity",
    "Problem-Solving Style",
    "Communication",
    "Leadership",
    "Teamwork",
    "Decision Making",
    "Persistence",
    "Confidence",
    "Academic Interests",
    "Career Interests",
    "Study Habits",
    "Motivation",
]

COGNITIVE_SKILL_PLAN = [
    "logical reasoning",
    "creativity",
    "critical thinking",
    "problem solving",
    "decision making",
    "analytical thinking",
    "observation",
    "pattern recognition",
]

COGNITIVE_FORMAT_PLAN = [
    "scenario",
    "multiple-choice",
    "short-response",
    "ranking",
    "best-solution",
    "situational-judgement",
]

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


def _normalise_question_text(value: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", value.lower()).strip()


def _questions_are_similar(first: str, second: str) -> bool:
    """Detect exact, near-copy, and strongly overlapping questions."""
    left = _normalise_question_text(first)
    right = _normalise_question_text(second)
    if not left or not right:
        return False
    if left == right:
        return True
    if SequenceMatcher(None, left, right).ratio() >= 0.78:
        return True
    left_words, right_words = set(left.split()), set(right.split())
    union = left_words | right_words
    return bool(union) and len(left_words & right_words) / len(union) >= 0.68


def _is_unique_question(question: str, existing_questions: list[str]) -> bool:
    return not any(
        _questions_are_similar(question, existing) for existing in existing_questions
    )


def _balanced_psychometric_questions(
    cards: list,
    *,
    count: int,
    seen_card_ids: set[str],
) -> list[dict]:
    """Pick unique cards across categories, not just random rows."""
    json_by_id = {card["id"]: card for card in PSYCHOMETRIC_CARDS}
    candidates: list[dict] = []

    # Prefer DB rows, enriched with category/display from the canonical JSON bank.
    for card in cards:
        source = json_by_id.get(card.card_id, {})
        candidates.append(
            {
                "id": f"psych_{card.card_id}",
                "type": "psychometric",
                "source": "database",
                "category": source.get("category", "Insight"),
                "cognitive_skill": None,
                "format": source.get("display", "choose"),
                "question": card.question,
                "options": card.options,
                "display": source.get("display", "choose"),
                "correct_key": None,
                "explanation": None,
            }
        )

    # If the DB is empty or incomplete, the versioned 400-card bank remains usable.
    existing_ids = {question["id"].removeprefix("psych_") for question in candidates}
    for source in PSYCHOMETRIC_CARDS:
        if source["id"] not in existing_ids:
            candidates.append(
                {
                    "id": f"psych_{source['id']}",
                    "type": "psychometric",
                    "source": "database",
                    "category": source.get("category", "Insight"),
                    "cognitive_skill": None,
                    "format": source.get("display", "choose"),
                    "question": source["question"],
                    "options": source["options"],
                    "display": source.get("display", "choose"),
                    "correct_key": None,
                    "explanation": None,
                }
            )

    candidates = [
        question
        for question in candidates
        if question["id"].removeprefix("psych_") not in seen_card_ids
    ]
    random.shuffle(candidates)

    selected: list[dict] = []
    selected_texts: list[str] = []
    covered_categories: set[str] = set()

    for target_category in PSYCHOMETRIC_CATEGORY_PLAN:
        if len(selected) >= count:
            break
        match = next(
            (
                question
                for question in candidates
                if question["category"] == target_category
                and question["category"] not in covered_categories
                and _is_unique_question(question["question"], selected_texts)
            ),
            None,
        )
        if match:
            selected.append(match)
            selected_texts.append(match["question"])
            covered_categories.add(match["category"])
            candidates.remove(match)

    for question in candidates:
        if len(selected) >= count:
            break
        if _is_unique_question(question["question"], selected_texts):
            selected.append(question)
            selected_texts.append(question["question"])
            covered_categories.add(question["category"])
    return selected


def build_adaptive_cognitive_prompt(
    *,
    count: int,
    shs_level: str,
    total_assessment_questions: int,
    existing_questions: list[str],
    covered_categories: list[str],
    skill_plan: list[str],
    format_plan: list[str],
) -> str:
    """Build the rich, session-aware prompt used for every cognitive request."""
    wording = {
        "SHS 1": "Use simple wording and familiar school, home, and community scenarios.",
        "SHS 2": "Use moderately challenging scenarios that require comparing evidence.",
        "SHS 3": "Use sophisticated but age-appropriate scenarios requiring deeper judgement.",
    }.get(shs_level, "Use clear, age-appropriate SHS wording.")
    previous = "\n".join(
        f"{index + 1}. {question}" for index, question in enumerate(existing_questions)
    ) or "None yet"
    positions = ", ".join(str(index * 2 + 2) for index in range(count))

    return f"""
Create {count} fresh cognitive-discovery questions for the Atlas Starter Arena.
This is a friendly adaptive learner discovery, NOT an examination and NOT a test
of memorised curriculum facts.

STUDENT AND SESSION CONTEXT
- Student SHS level: {shs_level}
- Current progress: {len(existing_questions)} questions have already been selected
  for a {total_assessment_questions}-question Starter Arena.
- Your questions will appear at alternating positions: {positions}.
- Psychometric categories already covered: {", ".join(covered_categories) or "none"}.
- Cognitive skills to assess next, in order: {", ".join(skill_plan)}.
- Formats to use, in order: {", ".join(format_plan)}.
- Level adaptation: {wording}

ALL QUESTIONS ALREADY ASKED OR SELECTED
{previous}

STRICT REQUIREMENTS
1. Each question must complement the existing assessment and reveal a new perspective.
2. Do not generate anything identical or substantially similar to any listed question.
3. Do not repeat the same scenario, opening phrase, skill, or option pattern.
4. Focus on how the learner reasons, creates, observes, decides, communicates, or solves.
5. Keep the tone warm and conversational; never call it a test or exam.
6. Use Ghanaian SHS-relevant everyday contexts without relying on specialist knowledge.
7. A short-response item has no options and no single correct answer.
8. Ranking items ask the learner to order four approaches by personal preference.
9. Scenario, best-solution, and situational-judgement items use four balanced options.
10. Return ONLY a valid JSON array with exactly {count} objects.

JSON SHAPE
[
  {{
    "id": "cognitive_1",
    "type": "cognitive",
    "source": "llm",
    "cognitive_skill": "{skill_plan[0] if skill_plan else "reasoning"}",
    "format": "scenario|multiple-choice|short-response|ranking|best-solution|situational-judgement",
    "domain": "Human-readable skill label",
    "question": "Conversational question",
    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
    "correct_key": null,
    "explanation": "A neutral encouraging sentence about what the response reveals"
  }}
]
""".strip()


def _get_fallback_cognitive_questions(count: int, shs_level: str) -> list[dict]:
    """Level-aware, non-academic fallbacks used only when the LLM is unavailable."""
    scenarios = [
        (
            "logical reasoning",
            "scenario",
            "Three classmates give different explanations for why a group project is late. What would you do first?",
            {"A": "Check the timeline and evidence", "B": "Choose the most confident speaker", "C": "Ask everyone to vote", "D": "Start over immediately"},
        ),
        (
            "creativity",
            "short-response",
            "Imagine your class has no electricity for a presentation. What creative way could you still share the idea clearly?",
            {},
        ),
        (
            "critical thinking",
            "best-solution",
            "A popular post makes a surprising claim but gives no source. Which response sounds most like you?",
            {"A": "Check reliable sources before sharing", "B": "Share it because many people liked it", "C": "Reject it without checking", "D": "Ask only one friend"},
        ),
        (
            "problem solving",
            "scenario",
            "Your study group has one hour but three difficult tasks. How would you organise the group?",
            {"A": "Prioritise and divide tasks by strengths", "B": "Let everyone attempt everything", "C": "Start with the easiest and ignore time", "D": "Wait for one person to lead"},
        ),
        (
            "decision making",
            "ranking",
            "Rank these things from most to least important when making a difficult decision.",
            {"A": "Evidence available", "B": "Possible consequences", "C": "Advice from people affected", "D": "How quickly a choice can be made"},
        ),
        (
            "analytical thinking",
            "multiple-choice",
            "A plan worked well twice but failed the third time. What would you examine first?",
            {"A": "What changed in the third situation", "B": "Who should be blamed", "C": "Whether to abandon every plan", "D": "Which result you liked most"},
        ),
        (
            "observation",
            "situational-judgement",
            "During a group discussion, one quiet member keeps writing useful notes but never speaks. What do you notice?",
            {"A": "They may contribute best after time to think", "B": "They have no ideas", "C": "They dislike the group", "D": "They should be ignored"},
        ),
        (
            "pattern recognition",
            "multiple-choice",
            "You notice you understand lessons better on days you explain them to someone else. What is the most useful next step?",
            {"A": "Build explanation into your study routine", "B": "Assume it was luck", "C": "Stop taking notes completely", "D": "Only study when someone asks"},
        ),
    ]
    level_prefix = {
        "SHS 1": "",
        "SHS 2": "Think about the evidence carefully. ",
        "SHS 3": "Consider both immediate and long-term effects. ",
    }.get(shs_level, "")
    result = []
    for index, (skill, question_format, question, options) in enumerate(scenarios[:count]):
        result.append(
            {
                "id": f"cognitive_fb_{index + 1}",
                "type": "cognitive",
                "source": "fallback",
                "cognitive_skill": skill,
                "format": question_format,
                "domain": skill.replace("-", " ").title(),
                "question": f"{level_prefix}{question}",
                "options": options,
                "correct_key": None,
                "explanation": "Thanks — your response helps Atlas understand how you approach situations.",
            }
        )
    return result


def _parse_json_array(response: str) -> list:
    response = response.strip()
    if response.startswith("```json"):
        response = response[7:]
    elif response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    parsed = json.loads(response.strip())
    return parsed if isinstance(parsed, list) else []


async def _generate_adaptive_cognitive_questions(
    *,
    count: int,
    shs_level: str,
    existing_questions: list[str],
    covered_categories: list[str],
    total_assessment_questions: int,
) -> list[dict]:
    skills = [COGNITIVE_SKILL_PLAN[i % len(COGNITIVE_SKILL_PLAN)] for i in range(count)]
    formats = [COGNITIVE_FORMAT_PLAN[i % len(COGNITIVE_FORMAT_PLAN)] for i in range(count)]
    prompt = build_adaptive_cognitive_prompt(
        count=count,
        shs_level=shs_level,
        total_assessment_questions=total_assessment_questions,
        existing_questions=existing_questions,
        covered_categories=covered_categories,
        skill_plan=skills,
        format_plan=formats,
    )
    response = await get_ai_response(
        [
            {"role": "system", "content": STARTER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )
    if not response:
        return []

    try:
        generated = _parse_json_array(response)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("Could not parse adaptive cognitive questions: %s", exc)
        return []

    accepted: list[dict] = []
    comparison_texts = list(existing_questions)
    allowed_formats = set(COGNITIVE_FORMAT_PLAN)
    for index, item in enumerate(generated):
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        if not question or not _is_unique_question(question, comparison_texts):
            continue
        question_format = str(item.get("format", formats[index % len(formats)]))
        if question_format not in allowed_formats:
            question_format = formats[index % len(formats)]
        options = item.get("options") or {}
        if question_format != "short-response" and not isinstance(options, dict):
            continue
        accepted_item = {
            "id": f"cognitive_ai_{index + 1}_{random.randint(1000, 9999)}",
            "type": "cognitive",
            "source": "llm",
            "cognitive_skill": str(
                item.get("cognitive_skill", skills[index % len(skills)])
            ),
            "format": question_format,
            "domain": str(item.get("domain", skills[index % len(skills)].title())),
            "question": question,
            "options": options if question_format != "short-response" else {},
            "correct_key": item.get("correct_key"),
            "explanation": str(
                item.get(
                    "explanation",
                    "Thanks — this helps Atlas understand how you think.",
                )
            ),
        }
        accepted.append(accepted_item)
        comparison_texts.append(question)
        if len(accepted) >= count:
            break
    return accepted


async def generate_starter_session(
    db: AsyncSession,
    user_id: str,
    shs_level: str = "SHS 1",
    programme: str = "General Science",
    psychometric_count: int = 6,
    academic_count: int = 6,
) -> dict:
    """
    Generate a balanced, level-aware Starter Arena session.

    Returns:
        dict with:
          - session_id: str
          - questions: strict psychometric/cognitive alternation
          - total_count: int
    """
    session_id = f"sa_{user_id}_{random.randint(10000, 99999)}"

    # ── 1. Load canonical psychometric bank and prior user responses ─────
    db_psych_cards = []
    try:
        result = await db.execute(
            select(PsychometricCard).order_by(PsychometricCard.card_id)
        )
        db_psych_cards = result.scalars().all()
    except Exception as e:
        logger.warning(f"Failed to fetch psychometric cards from DB: {e}")

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

    psych_questions = _balanced_psychometric_questions(
        db_psych_cards,
        count=psychometric_count,
        seen_card_ids=seen_card_ids,
    )

    # ── 2. Generate session-aware cognitive questions via the LLM ─────────
    existing_questions = [question["question"] for question in psych_questions]
    covered_categories = [question["category"] for question in psych_questions]
    cognitive_questions = await _generate_adaptive_cognitive_questions(
        count=academic_count,
        shs_level=shs_level,
        existing_questions=existing_questions,
        covered_categories=covered_categories,
        total_assessment_questions=psychometric_count + academic_count,
    )

    if len(cognitive_questions) < academic_count:
        candidate_fallbacks = _get_fallback_cognitive_questions(
            academic_count, shs_level
        )
        comparison = existing_questions + [
            question["question"] for question in cognitive_questions
        ]
        for fallback in candidate_fallbacks:
            if len(cognitive_questions) >= academic_count:
                break
            if _is_unique_question(fallback["question"], comparison):
                cognitive_questions.append(fallback)
                comparison.append(fallback["question"])

    # ── 3. Alternate naturally: DB insight → LLM cognition → repeat ───────
    questions = []
    total = max(len(psych_questions), len(cognitive_questions))
    for i in range(total):
        if i < len(psych_questions):
            questions.append(psych_questions[i])
        if i < len(cognitive_questions):
            questions.append(cognitive_questions[i])

    return {
        "session_id": session_id,
        "questions": questions,
        "total_count": len(questions),
    }


async def _background_ai_generation(
    user_id: str,
    shs_level: str,
    psychometric_count: int,
    academic_count: int,
    db_psych_cards: list,
    psych_questions: list,
) -> None:
    """
    Background task: generate richer questions via AI and cache them for the NEXT session.
    Runs after the Starter Arena has already started so the user isn't waiting.
    """
    try:
        logger.info(f"Background AI: generating {psychometric_count} psychometric + {academic_count} academic questions for {shs_level}")
        global _ai_question_cache

        # ── Psychometric AI (if DB didn't have enough) ────────────────────
        if len(db_psych_cards) < psychometric_count:
            all_existing = set()
            for c in db_psych_cards:
                all_existing.add(c.question)
            for q in psych_questions:
                all_existing.add(q.get("question", ""))
            for fb in _get_fallback_psych_questions(8):
                all_existing.add(fb["question"])
            existing_text = "\n".join(f"- {q}" for q in sorted(all_existing))

            ai_psych = await _generate_psychometric_questions(
                count=psychometric_count,
                existing_questions=existing_text,
            )
            if ai_psych:
                # Store in cache for NEXT session
                _ai_question_cache["psychometric"] = ai_psych
                logger.info(f"Background AI: cached {len(ai_psych)} psychometric questions")

        # ── Academic AI ───────────────────────────────────────────────────
        ai_academic = await _generate_academic_questions(
            count=academic_count,
            shs_level=shs_level,
        )
        if ai_academic:
            # Store in cache for NEXT session (keyed by SHS level)
            if shs_level not in _ai_question_cache["academic"]:
                _ai_question_cache["academic"][shs_level] = []
            _ai_question_cache["academic"][shs_level] = ai_academic
            logger.info(f"Background AI: cached {len(ai_academic)} academic questions for {shs_level}")

    except Exception as e:
        logger.warning(f"Background AI generation failed: {e}")


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
    """Build a learner profile instantly from psychometric + cognitive discovery data."""
    cognitive_responses = academic_responses
    all_responses = list(psychometric_responses) + list(cognitive_responses)

    avg_time = 0.0
    if all_responses:
        times = [float(r.get("time_taken") or r.get("time_taken_seconds") or 0) for r in all_responses]
        avg_time = sum(times) / len(times) if times else 0.0

    covered_categories = sorted(
        {
            str(r.get("category") or r.get("domain") or "").strip()
            for r in psychometric_responses
            if str(r.get("category") or r.get("domain") or "").strip()
        }
    )
    cognitive_skills = sorted(
        {
            str(r.get("cognitive_skill") or r.get("domain") or "").strip()
            for r in cognitive_responses
            if str(r.get("cognitive_skill") or r.get("domain") or "").strip()
        }
    )

    strengths: list[str] = []
    growth_areas: list[str] = []
    recommended_challenges: list[str] = []
    interests: list[str] = []

    for category in covered_categories:
        lowered = category.lower()
        if "creativ" in lowered:
            strengths.append("Creative thinking")
            recommended_challenges.append("Scientific Thinking")
        elif "leadership" in lowered:
            strengths.append("Leadership potential")
        elif "team" in lowered:
            strengths.append("Collaborative learning")
        elif "curiosity" in lowered or "research" in lowered:
            strengths.append("Curious explorer")
            recommended_challenges.append("Learning Center")
        elif "problem" in lowered:
            strengths.append("Practical problem-solving")
            recommended_challenges.append("Logic Arena")
        elif "decision" in lowered:
            strengths.append("Thoughtful decision-making")
        elif "career" in lowered or "academic interest" in lowered:
            interests.append(category)
        elif "confidence" in lowered or "persistence" in lowered:
            strengths.append("Growth mindset signals")

    for skill in cognitive_skills:
        lowered = skill.lower()
        if "logic" in lowered or "pattern" in lowered or "analytical" in lowered:
            strengths.append("Analytical reasoning")
            recommended_challenges.append("Logic Arena")
        elif "creat" in lowered:
            strengths.append("Imaginative problem framing")
        elif "critical" in lowered:
            strengths.append("Critical evaluation")
        elif "decision" in lowered:
            strengths.append("Judgement under uncertainty")
        elif "problem" in lowered:
            recommended_challenges.append("Problem Solving")

    if avg_time and avg_time < 18:
        strengths.append("Decisive response style")
    elif avg_time and avg_time >= 30:
        strengths.append("Reflective thinker")
        growth_areas.append("May benefit from timed practice for challenge arenas")

    if not strengths:
        strengths.append("Engaged learner ready for personalised guidance")
    if not growth_areas:
        growth_areas.append("Continue exploring adaptive challenges to reveal sharper strengths")
    if not recommended_challenges:
        recommended_challenges = ["Logic Arena", "Learning Center"]

    # Deduplicate while preserving order
    def _unique(items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            key = item.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result

    strengths = _unique(strengths)
    growth_areas = _unique(growth_areas)
    recommended_challenges = _unique(recommended_challenges + ["Daily Challenges"])
    interests = _unique(interests)

    learning_style = "Balanced"
    for response in psychometric_responses:
        question = str(response.get("question", "")).lower()
        answer = str(response.get("answer", "")).upper()
        if "understand" in question or "learn" in question or "study" in question:
            learning_style = {
                "A": "Visual",
                "B": "Auditory",
                "C": "Reading",
                "D": "Kinesthetic",
            }.get(answer[:1], learning_style)
            break

    confidence = "High" if len(all_responses) >= 10 and avg_time < 25 else "Medium"
    reasoning = (
        "High"
        if any("logic" in skill.lower() or "analytical" in skill.lower() for skill in cognitive_skills)
        else "Developing"
    )

    return {
        "learning_style": {
            "primary": learning_style,
            "description": (
                f"Your Starter Arena responses suggest a {learning_style.lower()} learning "
                "preference. Atlas will personalise Learning Centre paths, challenge difficulty, "
                "and future recommendations around how you think."
            ),
        },
        "academic_strengths": strengths + [f"Programme: {programme}"],
        "academic_weaknesses": growth_areas,
        "confidence_level": confidence,
        "reasoning_ability": reasoning,
        "recommended_focus": (
            f"For {shs_level}, Atlas will emphasise {cognitive_skills[0] if cognitive_skills else 'balanced reasoning'} "
            f"while nurturing your {learning_style.lower()} learning style across {programme}."
        ),
        "recommended_challenges": recommended_challenges,
        "recommendation_profile": (
            f"{shs_level} student in {programme}. Style: {learning_style}. "
            f"Covered psychometric categories: {', '.join(covered_categories) or 'general'}. "
            f"Cognitive skills observed: {', '.join(cognitive_skills) or 'emerging'}."
        ),
        "cognitive_skills": cognitive_skills,
        "psychometric_categories": covered_categories,
        "interests": interests,
        "response_count": len(all_responses),
        "average_response_seconds": round(avg_time, 1),
    }


