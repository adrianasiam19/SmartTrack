"""
challenge_hub.py — Atlas Adaptive Challenge Hub

Generates WASSCE-style challenge questions via AI for the 4 Core Subjects.
Manages session state, XP scoring (+5/-5), and adaptive difficulty.
"""
import asyncio
import json
import logging
import random
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assessment.models import ChallengeSession, ChallengeResponse
from app.assessment.starter_arena import get_ai_response
from app.users.models import User

logger = logging.getLogger(__name__)

# ── In-memory session store for active challenges ─────────────────────────
# AI-generated questions are cached here during the session (not persisted).
_challenge_sessions: dict = {}

# ── Core Subjects (exactly 4, in order) ────────────────────────────────────
CORE_SUBJECTS = [
    "Core Mathematics",
    "English Language",
    "Integrated Science",
    "Social Studies",
]

# ── Question types to vary across the 6 questions ──────────────────────────
QUESTION_TYPES = [
    "mcq",
    "mcq",
    "fill-blank",
    "true-false",
    "mcq",
    "scenario",
]

# ── Timer durations per challenge level ────────────────────────────────────
TIMER_SECONDS = {
    1: 120,  # 2 minutes
    2: 120,  # 2 minutes
    3: 180,  # 3 minutes
}

# ── XP scoring ─────────────────────────────────────────────────────────────
XP_CORRECT = 5
XP_WRONG = -5

# ── Fallback questions when AI fails ───────────────────────────────────────
FALLBACK_QUESTIONS = {
    "Core Mathematics": [
        {
            "id": "ch_math_fb_1",
            "question": "What is the value of 3² + 4²?",
            "options": {"A": "7", "B": "12", "C": "25", "D": "49"},
            "correct_answer": "C",
            "question_type": "mcq",
            "explanation": "3² = 9 and 4² = 16. 9 + 16 = 25.",
        },
        {
            "id": "ch_math_fb_2",
            "question": "Solve for x: 3x − 7 = 14",
            "options": {"A": "3", "B": "5", "C": "7", "D": "21"},
            "correct_answer": "C",
            "question_type": "mcq",
            "explanation": "3x − 7 = 14 → 3x = 21 → x = 7.",
        },
        {
            "id": "ch_math_fb_3",
            "question": "A bag contains 3 red, 5 blue, and 2 green marbles. What is the probability of picking a blue marble?",
            "options": {"A": "1/2", "B": "1/3", "C": "3/10", "D": "2/5"},
            "correct_answer": "A",
            "question_type": "mcq",
            "explanation": "Total marbles = 3 + 5 + 2 = 10. Blue marbles = 5. Probability = 5/10 = 1/2.",
        },
        {
            "id": "ch_math_fb_4",
            "question": "Complete: The sum of angles in a triangle is ______ degrees.",
            "options": {"A": "90", "B": "180", "C": "270", "D": "360"},
            "correct_answer": "B",
            "question_type": "fill-blank",
            "explanation": "The interior angles of any triangle always sum to 180°.",
        },
        {
            "id": "ch_math_fb_5",
            "question": "The gradient of a horizontal line is zero.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "A",
            "question_type": "true-false",
            "explanation": "A horizontal line has no vertical change, so its gradient (slope) is 0.",
        },
        {
            "id": "ch_math_fb_6",
            "question": "A student scored 45 out of 60 in a test. What is the percentage score?",
            "options": {"A": "65%", "B": "70%", "C": "75%", "D": "80%"},
            "correct_answer": "C",
            "question_type": "mcq",
            "explanation": "Percentage = (45/60) × 100 = 75%.",
        },
    ],
    "English Language": [
        {
            "id": "ch_eng_fb_1",
            "question": "Identify the figure of speech: 'The wind whispered through the trees.'",
            "options": {"A": "Simile", "B": "Metaphor", "C": "Personification", "D": "Hyperbole"},
            "correct_answer": "C",
            "question_type": "mcq",
            "explanation": "The wind is given the human action of whispering — this is personification.",
        },
        {
            "id": "ch_eng_fb_2",
            "question": "Choose the correct form: 'Neither the teacher nor the students ______ present.'",
            "options": {"A": "was", "B": "were", "C": "is", "D": "has"},
            "correct_answer": "B",
            "question_type": "mcq",
            "explanation": "When 'neither...nor' joins a singular and plural subject, the verb agrees with the nearest subject (students → were).",
        },
        {
            "id": "ch_eng_fb_3",
            "question": "Fill in the blank: She has been studying ______ three hours.",
            "options": {"A": "since", "B": "for", "C": "during", "D": "in"},
            "correct_answer": "B",
            "question_type": "fill-blank",
            "explanation": "'For' is used with a duration of time (three hours). 'Since' is used with a specific point in time.",
        },
        {
            "id": "ch_eng_fb_4",
            "question": "An adverb modifies a verb, adjective, or another adverb.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "A",
            "question_type": "true-false",
            "explanation": "Adverbs modify verbs (run quickly), adjectives (very tall), or other adverbs (quite easily).",
        },
        {
            "id": "ch_eng_fb_5",
            "question": "Which word is a synonym for 'benevolent'?",
            "options": {"A": "Malevolent", "B": "Kind", "C": "Hostile", "D": "Indifferent"},
            "correct_answer": "B",
            "question_type": "mcq",
            "explanation": "'Benevolent' means well-meaning and kindly — 'kind' is its synonym.",
        },
        {
            "id": "ch_eng_fb_6",
            "question": "Read the passage: 'The old man sat quietly by the window, watching the rain fall.' The mood created is one of:",
            "options": {"A": "Excitement", "B": "Tranquility", "C": "Anger", "D": "Confusion"},
            "correct_answer": "B",
            "question_type": "scenario",
            "explanation": "Words like 'quietly', 'watching the rain fall' convey a peaceful, tranquil mood.",
        },
    ],
    "Integrated Science": [
        {
            "id": "ch_sci_fb_1",
            "question": "Which organelle is known as the 'powerhouse of the cell'?",
            "options": {"A": "Nucleus", "B": "Ribosome", "C": "Mitochondrion", "D": "Golgi apparatus"},
            "correct_answer": "C",
            "question_type": "mcq",
            "explanation": "Mitochondria generate most of the cell's ATP through cellular respiration — hence 'powerhouse'.",
        },
        {
            "id": "ch_sci_fb_2",
            "question": "What is the chemical symbol for potassium?",
            "options": {"A": "Po", "B": "Pt", "C": "K", "D": "P"},
            "correct_answer": "C",
            "question_type": "mcq",
            "explanation": "K comes from the Latin word 'kalium'. Potassium's symbol is K.",
        },
        {
            "id": "ch_sci_fb_3",
            "question": "The boiling point of water at sea level is ______ °C.",
            "options": {"A": "90", "B": "100", "C": "110", "D": "212"},
            "correct_answer": "B",
            "question_type": "fill-blank",
            "explanation": "Water boils at 100°C (212°F) at standard atmospheric pressure at sea level.",
        },
        {
            "id": "ch_sci_fb_4",
            "question": "Sound travels faster in air than in water.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "B",
            "question_type": "true-false",
            "explanation": "Sound travels faster in denser media. It travels about 4.3× faster in water than in air.",
        },
        {
            "id": "ch_sci_fb_5",
            "question": "Which nutrient is the body's primary source of energy?",
            "options": {"A": "Protein", "B": "Carbohydrate", "C": "Fat", "D": "Vitamin"},
            "correct_answer": "B",
            "question_type": "mcq",
            "explanation": "Carbohydrates are broken down into glucose, which is the body's main energy source.",
        },
        {
            "id": "ch_sci_fb_6",
            "question": "A plant is placed in a dark room for a week. What will most likely happen?",
            "options": {"A": "It grows faster", "B": "It turns yellow", "C": "It flowers", "D": "No change"},
            "correct_answer": "B",
            "question_type": "scenario",
            "explanation": "Without light, chlorophyll breaks down and the plant cannot photosynthesise, causing it to turn yellow (etiolation).",
        },
    ],
    "Social Studies": [
        {
            "id": "ch_sst_fb_1",
            "question": "Which of the following is NOT a function of government?",
            "options": {"A": "Providing education", "B": "Maintaining law and order", "C": "Setting private business prices", "D": "Defending the country"},
            "correct_answer": "C",
            "question_type": "mcq",
            "explanation": "In a market economy, the government does not set private business prices — that's determined by supply and demand.",
        },
        {
            "id": "ch_sst_fb_2",
            "question": "What is the main purpose of the United Nations?",
            "options": {"A": "To control global trade", "B": "To maintain international peace and security", "C": "To set education standards", "D": "To create world laws"},
            "correct_answer": "B",
            "question_type": "mcq",
            "explanation": "The UN's primary purpose is maintaining international peace and security, though it also addresses humanitarian and development issues.",
        },
        {
            "id": "ch_sst_fb_3",
            "question": "Ghana's system of government is modelled after the ______ system.",
            "options": {"A": "Presidential", "B": "Parliamentary", "C": "Monarchical", "D": "Federal"},
            "correct_answer": "A",
            "question_type": "fill-blank",
            "explanation": "Ghana operates a presidential system of government, with an elected President as both Head of State and Government.",
        },
        {
            "id": "ch_sst_fb_4",
            "question": "Democracy means 'rule by the people'.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "A",
            "question_type": "true-false",
            "explanation": "Democracy comes from Greek 'demos' (people) and 'kratos' (rule) — literally 'rule by the people'.",
        },
        {
            "id": "ch_sst_fb_5",
            "question": "What is the main cause of deforestation in Ghana?",
            "options": {"A": "Urbanisation", "B": "Illegal logging and agriculture", "C": "Tourism", "D": "Mining only"},
            "correct_answer": "B",
            "question_type": "mcq",
            "explanation": "Illegal logging (galamsey) and expansion of agriculture (especially cocoa farming) are the primary causes of deforestation in Ghana.",
        },
        {
            "id": "ch_sst_fb_6",
            "question": "Which right allows citizens to vote in elections?",
            "options": {"A": "Economic right", "B": "Political right", "C": "Social right", "D": "Cultural right"},
            "correct_answer": "B",
            "question_type": "mcq",
            "explanation": "The right to vote is a fundamental political right that enables citizens to participate in choosing their leaders.",
        },
    ],
}

# ── AI Generation Prompt Templates ─────────────────────────────────────────

CHALLENGE_SYSTEM_PROMPT = (
    "You are an expert WASSCE question setter for the Ghana Education Service SHS curriculum. "
    "Generate high-quality, engaging questions that test understanding, not just memorisation. "
    "Follow WASSCE standards for question style and difficulty."
)

LEVEL_DESCRIPTIONS = {
    1: "EASY — Simple concepts, basic understanding, straightforward recall and application.",
    2: "MODERATE — Application-based questions requiring moderate reasoning and multi-step thinking.",
    3: "DIFFICULT — Challenging WASSCE-style questions requiring deeper understanding, critical thinking, and synthesis of multiple concepts.",
}

SHS_LEVEL_MAP = {
    "SHS 1": "SHS 1 (first year)",
    "SHS 2": "SHS 2 (second year)",
    "SHS 3": "SHS 3 (final year — WASSCE revision level)",
}

QUESTION_TYPE_LABELS = {
    "mcq": "Multiple choice (4 options A-D, choose one correct answer)",
    "fill-blank": "Fill in the blank / complete the statement",
    "true-false": "True or False statement",
    "scenario": "Scenario-based question (short passage or real-world situation to analyse)",
}


def _build_ai_prompt(subject: str, shs_level: str, challenge_level: int) -> str:
    """Build the AI prompt for generating 6 questions for one subject."""
    level_desc = LEVEL_DESCRIPTIONS.get(challenge_level, LEVEL_DESCRIPTIONS[1])
    shs_desc = SHS_LEVEL_MAP.get(shs_level, "SHS 1")
    question_types_str = "\n".join(
        f"  Question {i+1}: {QUESTION_TYPE_LABELS[qtype]}"
        for i, qtype in enumerate(QUESTION_TYPES)
    )

    prompt = f"""Generate exactly 6 {subject} questions for a {shs_desc} student.

DIFFICULTY LEVEL: {challenge_level} — {level_desc}

QUESTION TYPES (one per question, in order):
{question_types_str}

Each question must:
- Be appropriate for {shs_desc} level
- Match the {challenge_level} difficulty description above
- Include a clear, correct answer
- Include a helpful educational explanation (2-3 sentences)
- Be original and interesting (not a recycled standard question)

Return ONLY valid JSON array (no markdown, no code blocks):
[
  {{
    "id": "{subject.lower().replace(' ', '_')}_q1",
    "question": "Question text here",
    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
    "correct_answer": "A",
    "question_type": "mcq",
    "explanation": "Educational explanation why this answer is correct"
  }},
  ...
]

IMPORTANT:
- For fill-blank: options should be possible completions
- For true-false: options must be {{"A": "True", "B": "False"}}
- For scenario: include a brief scenario in the question text
- correct_answer must be "A", "B", "C", or "D" (matching one of the option keys)
- All 6 questions must be different and cover different topics within {subject}"""
    return prompt


async def _call_ai_for_subject(
    subject: str, shs_level: str, challenge_level: int
) -> list:
    """Call AI to generate 6 questions for one subject. Returns list of question dicts."""
    prompt = _build_ai_prompt(subject, shs_level, challenge_level)
    response = await get_ai_response([
        {"role": "system", "content": CHALLENGE_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])
    if not response:
        logger.warning(f"AI returned empty response for {subject}")
        return []

    try:
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        questions = json.loads(response)
        if not isinstance(questions, list):
            logger.warning(f"AI response for {subject} is not a list: {type(questions)}")
            return []
        return questions
    except Exception as e:
        logger.error(f"Failed to parse AI response for {subject}: {e}")
        return []


async def generate_subject_questions(
    subject: str, shs_level: str, challenge_level: int
) -> list:
    """Generate 6 questions for a subject. Tries AI first, falls back to hardcoded."""
    ai_questions = await _call_ai_for_subject(subject, shs_level, challenge_level)
    if len(ai_questions) >= 6:
        logger.info(f"AI generated {len(ai_questions)} questions for {subject}")
        return ai_questions[:6]

    # Fallback: use hardcoded questions
    logger.info(f"Using fallback questions for {subject} (AI returned {len(ai_questions)})")
    fallback = FALLBACK_QUESTIONS.get(subject, [])
    if not fallback:
        logger.error(f"No fallback questions for {subject}")
        return []

    # Shuffle fallback questions for variety, but keep deterministic enough
    shuffled = list(fallback)
    random.shuffle(shuffled)
    return shuffled[:6]


async def start_challenge_session(
    db: AsyncSession,
    user_id,
    shs_level: str,
    challenge_level: int = 1,
) -> dict:
    """
    Start a new Challenge Hub session.
    Generates all 24 questions (6 per subject) in parallel via AI.
    Creates a DB record and returns session data for the frontend.
    Returns instant fallback questions while AI generates in background.
    """
    # Create DB record
    db_session = ChallengeSession(
        user_id=user_id,
        challenge_level=challenge_level,
        status="in_progress",
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)

    session_id = str(db_session.id)

    # Try to generate all 4 subjects in parallel via AI
    subjects_data = {}
    try:
        tasks = [
            generate_subject_questions(subject, shs_level, challenge_level)
            for subject in CORE_SUBJECTS
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, subject in enumerate(CORE_SUBJECTS):
            result = results[i]
            if isinstance(result, Exception):
                logger.warning(f"Failed to generate {subject}: {result}")
                result = FALLBACK_QUESTIONS.get(subject, [])
            subjects_data[subject] = result
    except Exception as e:
        logger.error(f"Critical error in question generation: {e}")
        for subject in CORE_SUBJECTS:
            subjects_data[subject] = FALLBACK_QUESTIONS.get(subject, [])

    # Build the full question list for all subjects
    all_questions = {}
    for subject in CORE_SUBJECTS:
        questions = subjects_data.get(subject, [])
        # Ensure exactly 6 questions, properly formatted
        formatted = []
        for i, q in enumerate(questions[:6]):
            formatted.append({
                "id": q.get("id", f"{subject.lower().replace(' ', '_')}_{i+1}"),
                "question": q.get("question", ""),
                "options": q.get("options", {"A": "", "B": "", "C": "", "D": ""}),
                "correct_answer": q.get("correct_answer", "A"),
                "question_type": q.get("question_type", "mcq"),
                "explanation": q.get("explanation", ""),
            })
        all_questions[subject] = formatted

    # Store in-memory session
    _challenge_sessions[session_id] = {
        "session_id": session_id,
        "db_session_id": db_session.id,
        "user_id": user_id,
        "shs_level": shs_level,
        "challenge_level": challenge_level,
        "status": "in_progress",
        "current_subject_index": 0,
        "current_question_index": 0,
        "questions": all_questions,
        "responses": {},  # subject -> list of response dicts
        "total_xp": 0,
        "correct_count": 0,
        "wrong_count": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    # Return first question data to frontend
    first_subject = CORE_SUBJECTS[0]
    first_questions = all_questions.get(first_subject, [])

    return {
        "session_id": session_id,
        "challenge_level": challenge_level,
        "subjects": CORE_SUBJECTS,
        "current_subject": first_subject,
        "current_subject_index": 0,
        "current_question_index": 0,
        "questions": first_questions,
        "total_xp": 0,
        "timer_seconds": TIMER_SECONDS.get(challenge_level, 120),
    }


def get_current_subject_index(session_id: str) -> int | None:
    """Get the current subject index for a session."""
    session = _challenge_sessions.get(session_id)
    if not session:
        return None
    return session.get("current_subject_index", 0)


def get_session_data(session_id: str) -> dict | None:
    """Get the in-memory session data for a session."""
    return _challenge_sessions.get(session_id)


def get_current_questions(session_id: str, subject_index: int) -> dict | None:
    """Get the questions for a specific subject within a session."""
    session = _challenge_sessions.get(session_id)
    if not session:
        return None
    if subject_index >= len(CORE_SUBJECTS):
        return None

    subject = CORE_SUBJECTS[subject_index]
    questions = session["questions"].get(subject, [])
    session["current_subject_index"] = subject_index
    session["current_question_index"] = 0

    return {
        "session_id": session_id,
        "subject": subject,
        "subject_index": subject_index,
        "questions": questions,
        "timer_seconds": TIMER_SECONDS.get(session["challenge_level"], 120),
    }


def submit_answer(
    session_id: str,
    subject: str,
    question_index: int,
    user_answer: str,
    time_taken_seconds: float,
) -> dict | None:
    """Submit an answer, calculate XP, return feedback."""
    session = _challenge_sessions.get(session_id)
    if not session:
        return None

    questions = session["questions"].get(subject, [])
    if question_index >= len(questions):
        return None

    question = questions[question_index]
    correct_answer = question.get("correct_answer", "")
    is_correct = user_answer.strip().upper() == correct_answer.strip().upper()

    xp_change = XP_CORRECT if is_correct else XP_WRONG
    session["total_xp"] += xp_change
    if is_correct:
        session["correct_count"] += 1
    else:
        session["wrong_count"] += 1

    # Record response
    if subject not in session["responses"]:
        session["responses"][subject] = []
    session["responses"][subject].append({
        "question_index": question_index,
        "question_text": question.get("question", ""),
        "question_type": question.get("question_type", "mcq"),
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "time_taken_seconds": time_taken_seconds,
        "xp_earned": xp_change,
    })

    session["current_question_index"] = question_index + 1

    # Check if subject is complete
    subject_complete = question_index + 1 >= len(questions)
    current_subject_idx = CORE_SUBJECTS.index(subject)
    next_subject = None
    session_complete = False

    if subject_complete:
        next_idx = current_subject_idx + 1
        if next_idx >= len(CORE_SUBJECTS):
            session_complete = True
            session["status"] = "completed"
        else:
            next_subject = CORE_SUBJECTS[next_idx]
            session["current_subject_index"] = next_idx
            session["current_question_index"] = 0

    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "explanation": question.get("explanation", ""),
        "xp_earned": xp_change,
        "subject_complete": subject_complete,
        "session_complete": session_complete,
        "next_subject": next_subject,
        "total_xp": session["total_xp"],
        "current_question_index": session["current_question_index"],
    }


async def complete_session(
    db: AsyncSession, user_id, session_id: str
) -> dict:
    """
    Finalise a challenge session:
    1. Save all response data to DB
    2. Update user XP
    3. Calculate summary
    4. Return full summary
    """
    session = _challenge_sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    # Get the DB session record
    db_session = await db.get(ChallengeSession, session["db_session_id"])
    if not db_session:
        return {"error": "DB session not found"}

    # Save all responses to DB
    saved_count = 0
    for subject, responses in session["responses"].items():
        questions = session["questions"].get(subject, [])
        for resp in responses:
            qi = resp["question_index"]
            q_data = questions[qi] if qi < len(questions) else {}
            db_resp = ChallengeResponse(
                session_id=db_session.id,
                user_id=user_id,
                subject=subject,
                question_index=qi,
                question_text=resp["question_text"],
                question_type=resp["question_type"],
                options=q_data.get("options"),
                correct_answer=resp["correct_answer"],
                user_answer=resp["user_answer"],
                is_correct=resp["is_correct"],
                time_taken_seconds=resp["time_taken_seconds"],
                xp_earned=resp["xp_earned"],
                explanation=q_data.get("explanation", ""),
            )
            db.add(db_resp)
            saved_count += 1

    # Update session record
    db_session.status = "completed"
    db_session.total_xp = session["total_xp"]
    db_session.correct_count = session["correct_count"]
    db_session.wrong_count = session["wrong_count"]
    db_session.completed_at = datetime.now(timezone.utc)

    # Update user XP
    user = await db.get(User, user_id)
    if user:
        # Ensure XP doesn't go below 0
        new_xp = max(0, (user.xp or 0) + session["total_xp"])
        user.xp = new_xp

    await db.commit()

    # Calculate summary
    total_answered = session["correct_count"] + session["wrong_count"]
    accuracy = round((session["correct_count"] / total_answered * 100)) if total_answered > 0 else 0

    subject_performance = []
    for subject in CORE_SUBJECTS:
        responses = session["responses"].get(subject, [])
        correct = sum(1 for r in responses if r["is_correct"])
        total = len(responses)
        subject_performance.append({
            "subject": subject,
            "correct": correct,
            "total": total,
            "accuracy": round((correct / total * 100)) if total > 0 else 0,
            "xp": sum(r["xp_earned"] for r in responses),
        })

    # Determine strongest/weakest
    sorted_perf = sorted(subject_performance, key=lambda x: x["accuracy"], reverse=True)
    strongest = sorted_perf[0]["subject"] if sorted_perf else ""
    weakest = sorted_perf[-1]["subject"] if sorted_perf else ""

    # Weak topics = subjects with < 60% accuracy
    weak_topics = [s["subject"] for s in sorted_perf if s["accuracy"] < 60]

    summary = {
        "session_id": session_id,
        "challenge_level": session["challenge_level"],
        "total_xp": session["total_xp"],
        "correct_count": session["correct_count"],
        "wrong_count": session["wrong_count"],
        "accuracy": accuracy,
        "strongest_subject": strongest,
        "weakest_subject": weakest,
        "weak_topics": weak_topics,
        "subject_performance": subject_performance,
        "subjects_completed": len(CORE_SUBJECTS),
    }

    # Clean up in-memory session after some time (but keep it for now)
    # _challenge_sessions.pop(session_id, None)

    return summary


def get_session_summary(session_id: str) -> dict | None:
    """Get session summary from in-memory data (before persisting)."""
    session = _challenge_sessions.get(session_id)
    if not session:
        return None

    total_answered = session["correct_count"] + session["wrong_count"]
    accuracy = round((session["correct_count"] / total_answered * 100)) if total_answered > 0 else 0

    subject_performance = []
    for subject in CORE_SUBJECTS:
        responses = session["responses"].get(subject, [])
        correct = sum(1 for r in responses if r["is_correct"])
        total = len(responses)
        subject_performance.append({
            "subject": subject,
            "correct": correct,
            "total": total,
            "accuracy": round((correct / total * 100)) if total > 0 else 0,
            "xp": sum(r["xp_earned"] for r in responses),
        })

    sorted_perf = sorted(subject_performance, key=lambda x: x["accuracy"], reverse=True)

    return {
        "session_id": session_id,
        "challenge_level": session["challenge_level"],
        "total_xp": session["total_xp"],
        "correct_count": session["correct_count"],
        "wrong_count": session["wrong_count"],
        "accuracy": accuracy,
        "strongest_subject": sorted_perf[0]["subject"] if sorted_perf else "",
        "weakest_subject": sorted_perf[-1]["subject"] if sorted_perf else "",
        "weak_topics": [s["subject"] for s in sorted_perf if s["accuracy"] < 60],
        "subject_performance": subject_performance,
    }
