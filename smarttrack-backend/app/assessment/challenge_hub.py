"""
challenge_hub.py — Atlas Adaptive Challenge Hub

Generates WASSCE-style challenge questions via AI for the 4 Core Subjects.
Manages session state, XP scoring (+5/-5), and adaptive difficulty.

KEY DESIGN — Atlas Controls Question Types
The LLM does NOT randomly decide question types. Atlas explicitly assigns
a specific question type to each of the 6 questions per subject, then
instructs the LLM to generate that exact format. This ensures:
- The frontend always knows what UI to render
- The response structure is predictable
- Varied question types provide an engaging experience

Supported types: mcq, fill-blank, short-answer, true-false, matching, order, scenario
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
_challenge_sessions: dict = {}

# ── Core Subjects (exactly 4, in order) ────────────────────────────────────
CORE_SUBJECTS = [
    "Core Mathematics",
    "English Language",
    "Integrated Science",
    "Social Studies",
]

# ── Question types supported by the Challenge Hub ──────────────────────────
QUESTION_TYPES = [
    "mcq",
    "fill-blank",
    "short-answer",
    "true-false",
    "matching",
    "order",
    "scenario",
]

# ── Per-type format specifications used in prompts ─────────────────────────
QUESTION_TYPE_JSON_TEMPLATES = {
    "mcq": (
        '{\n'
        '  "id": "unique_id",\n'
        '  "question": "Question text (can include a short scenario/passage)",\n'
        '  "options": {"A": "First option", "B": "Second option", "C": "Third option", "D": "Fourth option"},\n'
        '  "correct_answer": "A",\n'
        '  "question_type": "mcq",\n'
        '  "explanation": "Educational explanation (2-3 sentences)"\n'
        '}'
    ),
    "fill-blank": (
        '{\n'
        '  "id": "unique_id",\n'
        '  "question": "Question text with _____ or ... marking the blank",\n'
        '  "correct_answer": "The word or phrase that completes the blank",\n'
        '  "question_type": "fill-blank",\n'
        '  "explanation": "Educational explanation (2-3 sentences)"\n'
        '}'
    ),
    "short-answer": (
        '{\n'
        '  "id": "unique_id",\n'
        '  "question": "Question that can be answered in one sentence or phrase",\n'
        '  "correct_answer": "The expected short answer",\n'
        '  "question_type": "short-answer",\n'
        '  "explanation": "Educational explanation (2-3 sentences)"\n'
        '}'
    ),
    "true-false": (
        '{\n'
        '  "id": "unique_id",\n'
        '  "question": "Statement that is either true or false",\n'
        '  "options": {"A": "True", "B": "False"},\n'
        '  "correct_answer": "A",\n'
        '  "question_type": "true-false",\n'
        '  "explanation": "Educational explanation (2-3 sentences)"\n'
        '}'
    ),
    "matching": (
        '{\n'
        '  "id": "unique_id",\n'
        '  "question": "Instructions telling the student what to match",\n'
        '  "left_items": ["Item A1", "Item A2", "Item A3", "Item A4"],\n'
        '  "right_items": ["Item B1", "Item B2", "Item B3", "Item B4"],\n'
        '  "correct_matches": {"0": "1", "1": "2", "2": "3", "3": "0"},\n'
        '  "question_type": "matching",\n'
        '  "explanation": "Educational explanation (2-3 sentences)"\n'
        '}'
    ),
    "order": (
        '{\n'
        '  "id": "unique_id",\n'
        '  "question": "Instructions telling the student what to arrange in the correct order",\n'
        '  "items": ["Step/item 1 as presented", "Step/item 2 as presented", "Step/item 3 as presented", "Step/item 4 as presented"],\n'
        '  "correct_order": [2, 0, 3, 1],\n'
        '  "question_type": "order",\n'
        '  "explanation": "Educational explanation (2-3 sentences)"\n'
        '}'
    ),
    "scenario": (
        '{\n'
        '  "id": "unique_id",\n'
        '  "question": "A short passage describing a scenario, followed by the question to answer",\n'
        '  "options": {"A": "First option", "B": "Second option", "C": "Third option", "D": "Fourth option"},\n'
        '  "correct_answer": "A",\n'
        '  "question_type": "scenario",\n'
        '  "explanation": "Educational explanation (2-3 sentences)"\n'
        '}'
    ),
}

QUESTION_TYPE_LABELS = {
    "mcq": "Multiple Choice — exactly 4 options (A, B, C, D)",
    "fill-blank": "Fill in the Blank — question has a _____ blank, answer is the missing text",
    "short-answer": "Short Answer — student writes a word or short phrase",
    "true-false": "True or False — exactly 2 options (A: True, B: False)",
    "matching": "Matching — 4 items in left column match 4 items in right column",
    "order": "Arrange in Correct Order — 4 items placed in the right sequence",
    "scenario": "Scenario-Based — short passage followed by a multiple-choice question with 4 options",
}

# ── Rotations: ensure a balanced mix within each subject's 6 questions ─────
# Each row is a sequence of 6 question types used for one subject.
# Atlas rotates these deterministically so the LLM does not decide.
QUESTION_TYPE_ROTATIONS = [
    ["mcq", "fill-blank", "true-false", "short-answer", "mcq", "scenario"],
    ["mcq", "true-false", "fill-blank", "mcq", "scenario", "short-answer"],
    ["fill-blank", "mcq", "short-answer", "scenario", "true-false", "mcq"],
    ["scenario", "mcq", "fill-blank", "true-false", "short-answer", "matching"],
    ["mcq", "scenario", "true-false", "fill-blank", "order", "mcq"],
    ["true-false", "mcq", "fill-blank", "scenario", "short-answer", "order"],
    ["fill-blank", "true-false", "mcq", "matching", "scenario", "short-answer"],
    ["short-answer", "mcq", "scenario", "true-false", "fill-blank", "order"],
    ["matching", "fill-blank", "mcq", "scenario", "true-false", "short-answer"],
    ["order", "mcq", "true-false", "fill-blank", "scenario", "short-answer"],
]

# ── Timer durations per challenge level ────────────────────────────────────
TIMER_SECONDS = {
    1: 180,  # 3 minutes (increased for short-answer/fill-blank)
    2: 180,  # 3 minutes
    3: 240,  # 4 minutes
}

# ── XP scoring ─────────────────────────────────────────────────────────────
XP_CORRECT = 5
XP_WRONG = -5

# ── AI Generation Prompt Templates ─────────────────────────────────────────

CHALLENGE_SYSTEM_PROMPT = (
    "You are an expert WASSCE question setter for the Ghana Education Service SHS curriculum. "
    "Generate high-quality, engaging questions that test understanding, not just memorisation. "
    "Follow WASSCE standards for question style and difficulty.\n\n"
    "CRITICAL: You MUST follow the exact JSON structure specified for EACH question type. "
    "Do NOT deviate from the given format. Each question's structure depends on its question_type."
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

# ── Retry limit for invalid AI responses ───────────────────────────────────
MAX_RETRIES_PER_QUESTION = 2


def _get_subject_rotation_index(subject: str) -> int:
    """Deterministically pick a rotation for a subject so the same subject
    gets a different rotation on each session."""
    return hash(subject + str(datetime.now(timezone.utc).date())) % len(QUESTION_TYPE_ROTATIONS)


def _build_ai_prompt(
    subject: str,
    shs_level: str,
    challenge_level: int,
    question_types: list[str],
) -> str:
    """Build the AI prompt that explicitly assigns a type to each of the 6 questions."""
    level_desc = LEVEL_DESCRIPTIONS.get(challenge_level, LEVEL_DESCRIPTIONS[1])
    shs_desc = SHS_LEVEL_MAP.get(shs_level, "SHS 1")

    # Build per-question instructions
    questions_spec = []
    for i, qtype in enumerate(question_types):
        tmpl = QUESTION_TYPE_JSON_TEMPLATES.get(qtype, QUESTION_TYPE_JSON_TEMPLATES["mcq"])
        label = QUESTION_TYPE_LABELS.get(qtype, qtype)
        questions_spec.append(
            f"  Question {i+1} — TYPE: {label}\n"
            f"    Return EXACTLY this JSON structure:\n"
            f"    {tmpl}"
        )

    question_types_str = "\n\n".join(questions_spec)

    prompt = f"""Generate exactly 6 questions for {subject} for a {shs_desc} student.

DIFFICULTY LEVEL: {challenge_level} — {level_desc}

IMPORTANT — Atlas has already chosen the TYPE for each question below.
You MUST follow the specified type and JSON structure for each one.
Do NOT change the question type — generate the exact format requested.

Here are the 6 questions to generate:

{question_types_str}

RULES:
- Each question must be appropriate for {shs_desc} level
- Match the {challenge_level} difficulty description above
- Include a clear, correct answer
- Include a helpful educational explanation (2-3 sentences)
- Be original and interesting (not a recycled standard question)
- Cover different topics within {subject} — do NOT repeat the same concept

Return ONLY valid JSON array (no markdown, no code blocks, no extra text):
[
  {{question 1 JSON}},
  {{question 2 JSON}},
  {{question 3 JSON}},
  {{question 4 JSON}},
  {{question 5 JSON}},
  {{question 6 JSON}}
]"""
    return prompt


def _validate_question_structure(question: dict) -> tuple[bool, str]:
    """Validate that a question dict matches the expected structure for its type.
    Returns (is_valid, error_message)."""
    qtype = _normalise_question_type(question.get("question_type", ""))
    question["question_type"] = qtype
    if qtype not in QUESTION_TYPES:
        return False, f"Unknown question_type: '{qtype}'"

    if not question.get("question"):
        return False, "Missing 'question' field"

    if not question.get("explanation"):
        return False, "Missing 'explanation' field"

    if not question.get("correct_answer"):
        return False, "Missing 'correct_answer' field"

    # ── Per-type validation ────────────────────────────────────────────────
    if qtype in ("mcq", "scenario"):
        options = question.get("options")
        if not options or not isinstance(options, dict):
            return False, f"'{qtype}' requires 'options' as a dict with exactly 4 entries (A, B, C, D)"
        if len(options) != 4:
            return False, f"'{qtype}' requires exactly 4 options (A, B, C, D), got {len(options)}"
        for letter in ("A", "B", "C", "D"):
            if letter not in options:
                return False, f"'{qtype}' missing option {letter}"
        # Validate correct_answer is one of the keys
        if question["correct_answer"] not in ("A", "B", "C", "D"):
            return False, f"'{qtype}' correct_answer must be 'A', 'B', 'C', or 'D' (letter key), got '{question['correct_answer']}'"

    elif qtype == "fill-blank":
        # Must have a blank marker in the question text
        question_text = question.get("question", "")
        if "____" not in question_text and "..." not in question_text and "___" not in question_text:
            return False, "'fill-blank' question text must contain a blank marker (_____ or ...)"
        # Should NOT have options
        if question.get("options"):
            return False, "'fill-blank' must NOT include options"

    elif qtype == "short-answer":
        # Should NOT have options
        if question.get("options"):
            return False, "'short-answer' must NOT include options"
        # correct_answer should be reasonably short
        answer = question.get("correct_answer", "")
        if len(answer) > 200:
            return False, f"'short-answer' correct_answer too long ({len(answer)} chars, max 200)"

    elif qtype == "true-false":
        options = question.get("options")
        if not options or not isinstance(options, dict):
            return False, "'true-false' requires 'options' as a dict with exactly 'A' and 'B'"
        if "A" not in options or "B" not in options or len(options) != 2:
            return False, "'true-false' options must be exactly {'A': 'True', 'B': 'False'}"
        # ENFORCE that A = True and B = False (frontend hardcodes this mapping)
        opt_a = str(options.get("A", "")).lower()
        opt_b = str(options.get("B", "")).lower()
        if "true" not in opt_a:
            return False, "'true-false' option A must contain 'True', got '" + str(options.get("A", "")) + "'"
        if "false" not in opt_b:
            return False, "'true-false' option B must contain 'False', got '" + str(options.get("B", "")) + "'"
        if question["correct_answer"] not in ("A", "B"):
            return False, "'true-false' correct_answer must be 'A' or 'B'"

    elif qtype == "matching":
        left_items = question.get("left_items")
        right_items = question.get("right_items")
        matches = question.get("correct_matches")
        if not left_items or not isinstance(left_items, list) or len(left_items) < 2:
            return False, "'matching' requires 'left_items' array with at least 2 items"
        if not right_items or not isinstance(right_items, list) or len(right_items) < 2:
            return False, "'matching' requires 'right_items' array with at least 2 items"
        if len(left_items) != len(right_items):
            return False, f"'matching' left_items ({len(left_items)}) and right_items ({len(right_items)}) must have same count"
        if not matches or not isinstance(matches, dict):
            return False, "'matching' requires 'correct_matches' as a dict mapping left index -> right index"
        # Validate indices
        for lidx, ridx in matches.items():
            try:
                li = int(lidx)
                ri = int(ridx)
                if li < 0 or li >= len(left_items):
                    return False, f"'matching' left index {li} out of range"
                if ri < 0 or ri >= len(right_items):
                    return False, f"'matching' right index {ri} out of range"
            except ValueError:
                return False, f"'matching' key/value in correct_matches must be integers, got '{lidx}': '{ridx}'"

    elif qtype == "order":
        items = question.get("items")
        correct_order = question.get("correct_order")
        if not items or not isinstance(items, list) or len(items) < 2:
            return False, "'order' requires 'items' array with at least 2 items"
        if not correct_order or not isinstance(correct_order, list) or len(correct_order) != len(items):
            return False, f"'order' requires 'correct_order' array with exactly {len(items)} indices"
        # Validate indices
        seen = set()
        for idx in correct_order:
            if not isinstance(idx, int):
                return False, f"'order' correct_order must contain integers, got {type(idx).__name__}"
            if idx < 0 or idx >= len(items):
                return False, f"'order' index {idx} out of range for {len(items)} items"
            if idx in seen:
                return False, f"'order' duplicate index {idx}"
            seen.add(idx)

    return True, ""


async def _generate_single_question(
    subject: str,
    shs_level: str,
    challenge_level: int,
    qtype: str,
    q_index: int,
) -> dict | None:
    """Generate a single question of a specific type with up to MAX_RETRIES attempts."""
    level_desc = LEVEL_DESCRIPTIONS.get(challenge_level, LEVEL_DESCRIPTIONS[1])
    shs_desc = SHS_LEVEL_MAP.get(shs_level, "SHS 1")
    tmpl = QUESTION_TYPE_JSON_TEMPLATES.get(qtype, QUESTION_TYPE_JSON_TEMPLATES["mcq"])
    label = QUESTION_TYPE_LABELS.get(qtype, qtype)

    prompt = f"""Generate exactly ONE question for {subject} for a {shs_desc} student.

DIFFICULTY LEVEL: {challenge_level} — {level_desc}

TYPE: {label}

You MUST return ONLY valid JSON with exactly this structure (no markdown, no code blocks):
{tmpl}

The question must:
- Be appropriate for {shs_desc} level
- Match the {challenge_level} difficulty
- Include a clear correct_answer
- Include an educational explanation (2-3 sentences)
- Be original

Return ONLY the JSON object, no extra text."""

    for attempt in range(MAX_RETRIES_PER_QUESTION + 1):
        try:
            response = await get_ai_response([
                {"role": "system", "content": CHALLENGE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])
            if not response:
                continue

            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            question = json.loads(response)

            # Ensure id and question_type are set
            if not question.get("id"):
                question["id"] = f"{subject.lower().replace(' ', '_')}_{q_index + 1}"
            question["question_type"] = qtype

            valid, error = _validate_question_structure(question)
            if valid:
                return question
            else:
                logger.warning(f"Attempt {attempt + 1} for {subject} Q{q_index + 1} ({qtype}) invalid: {error}")
                continue

        except json.JSONDecodeError as e:
            logger.warning(f"Attempt {attempt + 1} for {subject} Q{q_index + 1} ({qtype}) JSON parse error: {e}")
            continue
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} for {subject} Q{q_index + 1} ({qtype}) error: {e}")
            continue

    return None


async def _call_ai_for_subject(
    subject: str, shs_level: str, challenge_level: int
) -> list:
    """Generate 6 questions for one subject.
    Uses batch generation first, then falls back to per-question generation
    for any that fail validation."""
    question_types = _get_rotation_for_subject(subject)

    # ── 1. Try generating all 6 in one batch call ─────────────────────────
    prompt = _build_ai_prompt(subject, shs_level, challenge_level, question_types)
    response = await get_ai_response([
        {"role": "system", "content": CHALLENGE_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])
    if response:
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            batch_questions = json.loads(response)
            if not isinstance(batch_questions, list):
                batch_questions = []

            # Validate each question against its expected type
            valid_questions = []
            invalid_indices = []
            for i, q in enumerate(batch_questions[:6]):
                expected_type = question_types[i] if i < len(question_types) else "mcq"
                # Ensure type matches what Atlas assigned
                q["question_type"] = expected_type
                if not q.get("id"):
                    q["id"] = f"{subject.lower().replace(' ', '_')}_{i + 1}"

                valid, error = _validate_question_structure(q)
                if valid:
                    valid_questions.append(q)
                else:
                    logger.warning(f"Batch Q{i + 1} ({expected_type}) invalid: {error}")
                    invalid_indices.append(i)

            if invalid_indices:
                # ── 2. Regenerate invalid questions individually ────────
                logger.info(f"Regenerating {len(invalid_indices)} invalid questions for {subject}")
                gen_tasks = []
                for idx in invalid_indices:
                    gen_tasks.append(
                        _generate_single_question(
                            subject, shs_level, challenge_level,
                            question_types[idx], idx,
                        )
                    )
                regenerated = await asyncio.gather(*gen_tasks)

                # Insert regenerated questions at correct positions
                result_questions = list(batch_questions[:6])
                for idx, new_q in zip(invalid_indices, regenerated):
                    if new_q:
                        result_questions[idx] = new_q
                    # If still failed, we keep the invalid one (better than nothing)

                # Final validation pass
                validated = []
                for q in result_questions[:6]:
                    expected_type = question_types[len(validated)]
                    q["question_type"] = expected_type
                    v, _ = _validate_question_structure(q)
                    if v:
                        validated.append(q)
                    else:
                        # Keep it anyway as last resort
                        validated.append(q)
                if len(validated) >= 4:
                    return validated[:6]

            if len(valid_questions) >= 4:
                return valid_questions[:6]

        except Exception as e:
            logger.error(f"Failed to parse batch AI response for {subject}: {e}")

    # ── 3. Fallback: generate each question individually ───────────────────
    logger.info(f"Generating questions individually for {subject}")
    tasks = [
        _generate_single_question(subject, shs_level, challenge_level, qtype, i)
        for i, qtype in enumerate(question_types)
    ]
    results = await asyncio.gather(*tasks)

    # Filter out None (failed) questions
    questions = [q for q in results if q is not None]

    # If we still don't have enough, pad with fallback
    if len(questions) < 6:
        logger.warning(f"Only generated {len(questions)} valid questions for {subject}; will pad with fallback")

    return questions[:6]


def _get_rotation_for_subject(subject: str) -> list[str]:
    """Pick a rotation for the subject based on today's date + subject name."""
    idx = _get_subject_rotation_index(subject)
    return QUESTION_TYPE_ROTATIONS[idx]


async def generate_subject_questions(
    subject: str, shs_level: str, challenge_level: int
) -> list:
    """Generate 6 questions for a subject. Tries AI first, falls back to hardcoded."""
    ai_questions = await _call_ai_for_subject(subject, shs_level, challenge_level)

    # Count valid questions
    valid_count = sum(1 for q in ai_questions if q and q.get("question"))
    if valid_count >= 4:
        logger.info(f"AI generated {valid_count} valid questions for {subject}")
        # Pad with fallback if less than 6
        if len(ai_questions) < 6:
            fallback = list(FALLBACK_QUESTIONS.get(subject, []))
            while len(ai_questions) < 6 and fallback:
                fb = fallback.pop(0)
                ai_questions.append(fb)
        return ai_questions[:6]

    # Fallback: use hardcoded questions
    logger.info(f"Using fallback questions for {subject} (AI returned {valid_count} valid)")
    fallback = FALLBACK_QUESTIONS.get(subject, [])
    if not fallback:
        logger.error(f"No fallback questions for {subject}")
        return []

    shuffled = list(fallback)
    random.shuffle(shuffled)
    return shuffled[:6]


async def start_challenge_session(
    db: AsyncSession,
    user_id,
    shs_level: str,
    challenge_level: int = 1,
) -> dict:
    """Start a new Challenge Hub session."""
    db_session = ChallengeSession(
        user_id=user_id,
        challenge_level=challenge_level,
        status="in_progress",
    )
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)

    session_id = str(db_session.id)

    async def _gen_one(subject: str) -> tuple:
        try:
            result = await generate_subject_questions(subject, shs_level, challenge_level)
            if not result:
                logger.warning(f"AI returned no questions for {subject}; using fallback.")
                result = FALLBACK_QUESTIONS.get(subject, [])
        except Exception as e:
            logger.warning(f"Failed to generate {subject}: {e}")
            result = FALLBACK_QUESTIONS.get(subject, [])
        return subject, result

    subjects_data = {}
    results = await asyncio.gather(
        *[_gen_one(s) for s in CORE_SUBJECTS],
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception):
            logger.warning(f"Subject generation raised: {r}")
            continue
        subject, data = r
        subjects_data[subject] = data

    all_questions = {}
    for subject in CORE_SUBJECTS:
        questions = subjects_data.get(subject, [])
        formatted = []
        for i, q in enumerate(questions[:6]):
            formatted.append(_format_question(q, subject, i))
        all_questions[subject] = formatted

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
        "responses": {},
        "level_archives": [],
        "total_xp": 0,
        # How much of total_xp has already been written to user.xp (avoids double-credit).
        "xp_credited": 0,
        "correct_count": 0,
        "wrong_count": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

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
        "timer_seconds": TIMER_SECONDS.get(challenge_level, 180),
    }


def _normalise_question_type(raw_type: str | None) -> str:
    """Map LLM variants (underscores, aliases) onto the canonical frontend types."""
    if not raw_type:
        return "mcq"
    key = str(raw_type).strip().lower().replace("_", "-").replace(" ", "-")
    aliases = {
        "truefalse": "true-false",
        "true-or-false": "true-false",
        "fillblank": "fill-blank",
        "fill-in-the-blank": "fill-blank",
        "fill-in-blank": "fill-blank",
        "shortanswer": "short-answer",
        "short-ans": "short-answer",
        "multiple-choice": "mcq",
        "multiplechoice": "mcq",
        "arrange": "order",
        "arrange-in-order": "order",
        "ordering": "order",
        "match": "matching",
        "interpretation": "scenario",
        "comprehension": "scenario",
    }
    key = aliases.get(key, key)
    if key not in QUESTION_TYPES:
        return "mcq"
    return key


def _format_question(q: dict, subject: str, index: int) -> dict:
    """Normalise a question dict into the standard format for the frontend."""
    qtype = _normalise_question_type(q.get("question_type", "mcq"))
    # If the model returned options but labelled it as fill/short, treat as mcq/scenario
    options = q.get("options")
    if qtype in ("fill-blank", "short-answer") and isinstance(options, dict) and len(options) >= 2:
        qtype = "mcq" if len(options) >= 4 else "true-false"

    formatted = {
        "id": q.get("id", f"{subject.lower().replace(' ', '_')}_{index + 1}"),
        "question": q.get("question", ""),
        "question_type": qtype,
        "explanation": q.get("explanation", ""),
    }

    if qtype in ("mcq", "scenario"):
        formatted["options"] = options if isinstance(options, dict) else {"A": "", "B": "", "C": "", "D": ""}
        formatted["correct_answer"] = q.get("correct_answer", "")
    elif qtype == "true-false":
        # Normalise: guarantee A="True", B="False" and adjust correct_answer
        raw_opts = options if isinstance(options, dict) else {}
        raw_answer = str(q.get("correct_answer", "A"))
        opt_a = str(raw_opts.get("A", "")).lower()
        opt_b = str(raw_opts.get("B", "")).lower()
        # Also accept literal True/False as the answer value
        if raw_answer.strip().lower() in ("true", "false"):
            raw_answer = "A" if raw_answer.strip().lower() == "true" else "B"
        if "true" in opt_b and "false" in opt_a:
            # AI swapped them: B is True, A is False → swap back
            formatted["options"] = {"A": "True", "B": "False"}
            formatted["correct_answer"] = "A" if raw_answer.upper() == "B" else "B"
        else:
            formatted["options"] = {"A": "True", "B": "False"}
            formatted["correct_answer"] = raw_answer.upper() if raw_answer.upper() in ("A", "B") else "A"
    elif qtype in ("fill-blank", "short-answer"):
        formatted["options"] = None
        formatted["correct_answer"] = q.get("correct_answer", "")
    elif qtype == "matching":
        formatted["left_items"] = q.get("left_items", [])
        formatted["right_items"] = q.get("right_items", [])
        formatted["correct_matches"] = q.get("correct_matches", {})
        formatted["correct_answer"] = json.dumps(q.get("correct_matches", {}), sort_keys=True)
        formatted["options"] = None
    elif qtype == "order":
        formatted["items"] = q.get("items", [])
        formatted["correct_order"] = q.get("correct_order", [])
        formatted["correct_answer"] = json.dumps(q.get("correct_order", []))
        formatted["options"] = None

    return formatted


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
        "timer_seconds": TIMER_SECONDS.get(session["challenge_level"], 180),
    }


def submit_answer(
    session_id: str,
    subject: str,
    question_index: int,
    user_answer: str,
    time_taken_seconds: float,
) -> dict | None:
    """Submit an answer, calculate XP, return feedback.
    Handles all question types for comparison."""
    session = _challenge_sessions.get(session_id)
    if not session:
        return None

    questions = session.get("questions", {}).get(subject, [])
    if not questions or question_index >= len(questions):
        logger.warning(
            f"submit_answer: question_index {question_index} out of range "
            f"for {subject} (len={len(questions)})"
        )
        return None

    question = questions[question_index]
    if not question:
        logger.warning(f"submit_answer: question at index {question_index} is None/empty")
        return None

    # Prevent double-submit for the same question index
    existing = session.get("responses", {}).get(subject, [])
    if any(r.get("question_index") == question_index for r in existing):
        logger.warning(
            f"submit_answer: duplicate submit for {subject} Q{question_index} — ignoring"
        )
        return None

    correct_answer = question.get("correct_answer", "")
    qtype = question.get("question_type", "mcq")

    # ── Determine if answer is correct based on question type ────────
    is_correct = False
    try:
        if qtype in ("mcq", "scenario", "true-false"):
            is_correct = user_answer.strip().upper() == correct_answer.strip().upper()

        elif qtype in ("fill-blank", "short-answer"):
            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

        elif qtype == "matching":
            try:
                user_matches = json.loads(user_answer) if user_answer else {}
                correct_matches = json.loads(correct_answer) if correct_answer else {}
                # Normalise keys to strings for stable comparison
                user_norm = {str(k): str(v) for k, v in user_matches.items()}
                correct_norm = {str(k): str(v) for k, v in correct_matches.items()}
                is_correct = user_norm == correct_norm
            except (json.JSONDecodeError, TypeError, AttributeError):
                logger.warning(
                    f"Matching JSON parse error: user='{str(user_answer)[:50]}', "
                    f"correct='{str(correct_answer)[:50]}'"
                )
                is_correct = False

        elif qtype == "order":
            try:
                user_order = json.loads(user_answer) if user_answer else []
                correct_order = json.loads(correct_answer) if correct_answer else []
                is_correct = list(user_order) == list(correct_order)
            except (json.JSONDecodeError, TypeError):
                logger.warning(
                    f"Order JSON parse error: user='{str(user_answer)[:50]}', "
                    f"correct='{str(correct_answer)[:50]}'"
                )
                is_correct = False
        else:
            logger.warning(f"Unknown question_type '{qtype}', defaulting to letter comparison")
            is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
    except Exception as e:
        logger.warning(f"Answer comparison error for type {qtype}: {e}")
        is_correct = False

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
        "question_type": qtype,
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
    level_complete = False

    if subject_complete:
        next_idx = current_subject_idx + 1
        if next_idx >= len(CORE_SUBJECTS):
            if session["challenge_level"] >= 3:
                session_complete = True
                session["status"] = "completed"
            else:
                level_complete = True
                session["status"] = "level_complete"
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
        "level_complete": level_complete,
        "session_complete": session_complete,
        "next_subject": next_subject,
        "total_xp": session["total_xp"],
        "current_question_index": session["current_question_index"],
    }


async def continue_challenge_level(
    db: AsyncSession,
    user_id,
    session_id: str,
) -> dict:
    """Generate the next challenge level's 24 questions when the student chooses to continue."""
    session = _challenge_sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    if session["user_id"] != user_id:
        return {"error": "Unauthorized"}

    if session["status"] != "level_complete":
        return {"error": "Current level is not ready to continue"}

    if session["challenge_level"] >= 3:
        return {"error": "No further challenge levels available"}

    next_level = session["challenge_level"] + 1
    db_session = await db.get(ChallengeSession, session["db_session_id"])
    if not db_session:
        return {"error": "DB session not found"}

    db_session.challenge_level = next_level
    await db.commit()
    await db.refresh(db_session)

    # Archive the completed level so Level 2/3 can reuse question indices 0..5
    # without colliding with Level 1's recorded responses (which caused submit 404s).
    archives = session.setdefault("level_archives", [])
    archives.append(
        {
            "challenge_level": session["challenge_level"],
            "questions": session.get("questions", {}),
            "responses": session.get("responses", {}),
        }
    )

    session["challenge_level"] = next_level
    session["status"] = "in_progress"
    session["current_subject_index"] = 0
    session["current_question_index"] = 0
    session["responses"] = {}
    session["questions"] = {}

    async def _gen_one(subject: str) -> tuple:
        try:
            result = await generate_subject_questions(subject, session["shs_level"], next_level)
            if not result:
                logger.warning(f"AI returned no questions for {subject} on level {next_level}; using fallback.")
                result = FALLBACK_QUESTIONS.get(subject, [])
        except Exception as e:
            logger.warning(f"Failed to generate {subject} for level {next_level}: {e}")
            result = FALLBACK_QUESTIONS.get(subject, [])
        return subject, result

    subjects_data = {}
    results = await asyncio.gather(
        *[_gen_one(s) for s in CORE_SUBJECTS],
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception):
            logger.warning(f"Subject generation raised: {r}")
            continue
        subject, data = r
        subjects_data[subject] = data

    all_questions = {}
    for subject in CORE_SUBJECTS:
        questions = subjects_data.get(subject, [])
        formatted = []
        for i, q in enumerate(questions[:6]):
            formatted.append(_format_question(q, subject, i))
        all_questions[subject] = formatted

    session["questions"] = all_questions

    first_subject = CORE_SUBJECTS[0]
    first_questions = all_questions.get(first_subject, [])

    return {
        "session_id": session_id,
        "challenge_level": next_level,
        "current_subject": first_subject,
        "current_subject_index": 0,
        "current_question_index": 0,
        "questions": first_questions,
        "total_xp": session["total_xp"],
        "timer_seconds": TIMER_SECONDS.get(next_level, 180),
    }


def _iter_level_snapshots(session: dict) -> list[dict]:
    """Yield archived levels plus the current in-progress level as snapshots."""
    snapshots = list(session.get("level_archives") or [])
    snapshots.append(
        {
            "challenge_level": session.get("challenge_level"),
            "questions": session.get("questions", {}),
            "responses": session.get("responses", {}),
        }
    )
    return snapshots


def _aggregate_subject_performance(session: dict) -> list[dict]:
    """Merge answers across all challenge levels for summary stats."""
    totals: dict[str, dict] = {
        subject: {"correct": 0, "total": 0, "xp": 0} for subject in CORE_SUBJECTS
    }
    for snapshot in _iter_level_snapshots(session):
        for subject in CORE_SUBJECTS:
            responses = (snapshot.get("responses") or {}).get(subject, [])
            totals[subject]["correct"] += sum(1 for r in responses if r.get("is_correct"))
            totals[subject]["total"] += len(responses)
            totals[subject]["xp"] += sum(int(r.get("xp_earned") or 0) for r in responses)

    subject_performance = []
    for subject in CORE_SUBJECTS:
        data = totals[subject]
        total = data["total"]
        subject_performance.append(
            {
                "subject": subject,
                "correct": data["correct"],
                "total": total,
                "accuracy": round((data["correct"] / total * 100)) if total else 0,
                "xp": data["xp"],
            }
        )
    return subject_performance


async def credit_pending_xp(
    db: AsyncSession, user_id, session_id: str
) -> dict:
    """
    Persist any uncredited session XP onto the user profile.

    Safe to call multiple times: only total_xp - xp_credited is applied.
    Called when a challenge level completes (L1/L2) and again on /complete
    so exiting before L3 still keeps earned XP.
    """
    session = _challenge_sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    if session["user_id"] != user_id:
        return {"error": "Unauthorized"}

    total_xp = int(session.get("total_xp") or 0)
    already_credited = int(session.get("xp_credited") or 0)
    delta = total_xp - already_credited

    db_session = await db.get(ChallengeSession, session["db_session_id"])
    if db_session:
        db_session.total_xp = total_xp
        db_session.correct_count = session.get("correct_count", 0)
        db_session.wrong_count = session.get("wrong_count", 0)

    user = await db.get(User, user_id)
    user_xp = None
    if user:
        if delta != 0:
            user.xp = max(0, (user.xp or 0) + delta)
        from app.users.gamification import rank_for_xp

        user.rank = rank_for_xp(user.xp or 0)
        user_xp = user.xp or 0

    session["xp_credited"] = total_xp
    await db.commit()

    return {
        "xp_credited_delta": delta,
        "total_xp": total_xp,
        "user_xp": user_xp,
    }


async def complete_session(
    db: AsyncSession, user_id, session_id: str
) -> dict:
    """Finalise a challenge session: save to DB, update XP, return summary."""
    session = _challenge_sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    db_session = await db.get(ChallengeSession, session["db_session_id"])
    if not db_session:
        return {"error": "DB session not found"}

    saved_count = 0
    for snapshot in _iter_level_snapshots(session):
        level = snapshot.get("challenge_level")
        questions_by_subject = snapshot.get("questions") or {}
        for subject, responses in (snapshot.get("responses") or {}).items():
            questions = questions_by_subject.get(subject, [])
            for resp in responses:
                qi = resp["question_index"]
                q_data = questions[qi] if qi < len(questions) else {}
                # Namespace question_index by level so L1 Q0 and L2 Q0 do not collide
                # when reviewing saved history for the same session.
                stored_index = int(qi) + (int(level or 1) - 1) * 100
                db_resp = ChallengeResponse(
                    session_id=db_session.id,
                    user_id=user_id,
                    subject=subject,
                    question_index=stored_index,
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

    db_session.status = "completed"
    db_session.total_xp = session["total_xp"]
    db_session.correct_count = session["correct_count"]
    db_session.wrong_count = session["wrong_count"]
    db_session.completed_at = datetime.now(timezone.utc)

    # Credit any XP not already persisted at L1/L2 level_complete.
    credit = await credit_pending_xp(db, user_id, session_id)
    if "error" in credit:
        # credit_pending_xp already committed session row updates above via its own path;
        # fall back to a commit of response rows if credit somehow fails identity checks.
        await db.commit()
        return {"error": credit["error"]}

    total_answered = session["correct_count"] + session["wrong_count"]
    accuracy = round((session["correct_count"] / total_answered * 100)) if total_answered > 0 else 0

    subject_performance = _aggregate_subject_performance(session)
    sorted_perf = sorted(subject_performance, key=lambda x: x["accuracy"], reverse=True)
    strongest = sorted_perf[0]["subject"] if sorted_perf else ""
    weakest = sorted_perf[-1]["subject"] if sorted_perf else ""
    weak_topics = [s["subject"] for s in sorted_perf if s["accuracy"] < 60]

    summary = {
        "session_id": session_id,
        "challenge_level": session["challenge_level"],
        "total_xp": session["total_xp"],
        "xp_credited_delta": credit.get("xp_credited_delta", 0),
        "user_xp": credit.get("user_xp"),
        "correct_count": session["correct_count"],
        "wrong_count": session["wrong_count"],
        "accuracy": accuracy,
        "strongest_subject": strongest,
        "weakest_subject": weakest,
        "weak_topics": weak_topics,
        "subject_performance": subject_performance,
        "subjects_completed": len(CORE_SUBJECTS),
        "responses_saved": saved_count,
    }

    return summary


def get_session_summary(session_id: str) -> dict | None:
    """Get session summary from in-memory data (before persisting)."""
    session = _challenge_sessions.get(session_id)
    if not session:
        return None

    total_answered = session["correct_count"] + session["wrong_count"]
    accuracy = round((session["correct_count"] / total_answered * 100)) if total_answered > 0 else 0

    subject_performance = _aggregate_subject_performance(session)
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


# ══════════════════════════════════════════════════════════════════════════
#  FALLBACK QUESTIONS — each subject has 6+ varied-type fallback questions
# ══════════════════════════════════════════════════════════════════════════

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
            "question": "The sum of angles in a triangle is ______ degrees.",
            "correct_answer": "180",
            "question_type": "fill-blank",
            "explanation": "The interior angles of any triangle always sum to 180°.",
        },
        {
            "id": "ch_math_fb_3",
            "question": "The gradient of a horizontal line is zero.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "A",
            "question_type": "true-false",
            "explanation": "A horizontal line has no vertical change, so its gradient (slope) is 0.",
        },
        {
            "id": "ch_math_fb_4",
            "question": "What is the formula for the area of a circle?",
            "correct_answer": "πr²",
            "question_type": "short-answer",
            "explanation": "The area of a circle is π times the radius squared (πr²).",
        },
        {
            "id": "ch_math_fb_5",
            "question": "A bag contains 3 red, 5 blue, and 2 green marbles. What is the probability of picking a blue marble?",
            "options": {"A": "1/2", "B": "1/3", "C": "3/10", "D": "2/5"},
            "correct_answer": "A",
            "question_type": "mcq",
            "explanation": "Total marbles = 3 + 5 + 2 = 10. Blue marbles = 5. Probability = 5/10 = 1/2.",
        },
        {
            "id": "ch_math_fb_6",
            "question": "A student scored 45 out of 60 in a test. She wants to know her percentage score.",
            "options": {"A": "65%", "B": "70%", "C": "75%", "D": "80%"},
            "correct_answer": "C",
            "question_type": "scenario",
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
            "question": "She has been studying ______ three hours.",
            "correct_answer": "for",
            "question_type": "fill-blank",
            "explanation": "'For' is used with a duration of time. 'Since' is used with a specific point in time.",
        },
        {
            "id": "ch_eng_fb_3",
            "question": "An adverb modifies a verb, adjective, or another adverb.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "A",
            "question_type": "true-false",
            "explanation": "Adverbs modify verbs (run quickly), adjectives (very tall), or other adverbs (quite easily).",
        },
        {
            "id": "ch_eng_fb_4",
            "question": "What is the past tense of 'go'?",
            "correct_answer": "went",
            "question_type": "short-answer",
            "explanation": "'Go' is an irregular verb — its past tense is 'went'.",
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
            "question": "The old man sat quietly by the window, watching the rain fall. The mood created in this passage is one of:",
            "options": {"A": "Excitement", "B": "Tranquility", "C": "Anger", "D": "Confusion"},
            "correct_answer": "B",
            "question_type": "scenario",
            "explanation": "Words like 'quietly' and 'watching the rain fall' convey a peaceful, tranquil mood.",
        },
        {
            "id": "ch_eng_fb_7",
            "question": "Match each literary device to its correct definition.",
            "left_items": ["Simile", "Metaphor", "Personification", "Alliteration"],
            "right_items": ["Giving human qualities to non-human things", "Using 'like' or 'as' to compare", "Same starting sound in nearby words", "Direct comparison without 'like' or 'as'"],
            "correct_matches": {"0": "1", "1": "3", "2": "0", "3": "2"},
            "correct_answer": '{"0":"1","1":"3","2":"0","3":"2"}',
            "question_type": "matching",
            "explanation": "A simile uses 'like/as', a metaphor is a direct comparison, personification gives human traits to objects, alliteration repeats starting sounds.",
        },
        {
            "id": "ch_eng_fb_8",
            "question": "Arrange these steps for writing an essay in the correct order.",
            "items": ["Write the conclusion", "Brainstorm ideas", "Write the introduction", "Write body paragraphs", "Revise and edit"],
            "correct_order": [1, 2, 4, 3, 0],
            "correct_answer": "[1, 2, 4, 3, 0]",
            "question_type": "order",
            "explanation": "First brainstorm ideas, then write the introduction, then body paragraphs, then conclusion, and finally revise and edit.",
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
            "question": "The boiling point of water at sea level is ______ °C.",
            "correct_answer": "100",
            "question_type": "fill-blank",
            "explanation": "Water boils at 100°C (212°F) at standard atmospheric pressure at sea level.",
        },
        {
            "id": "ch_sci_fb_3",
            "question": "Sound travels faster in air than in water.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "B",
            "question_type": "true-false",
            "explanation": "Sound travels faster in denser media — about 4.3× faster in water than in air.",
        },
        {
            "id": "ch_sci_fb_4",
            "question": "What gas do plants absorb during photosynthesis?",
            "correct_answer": "Carbon dioxide",
            "question_type": "short-answer",
            "explanation": "Plants absorb carbon dioxide (CO₂) from the atmosphere and convert it into glucose and oxygen using sunlight.",
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
            "question": "Ghana's system of government is modelled after the ______ system.",
            "correct_answer": "Presidential",
            "question_type": "fill-blank",
            "explanation": "Ghana operates a presidential system of government with an elected President as both Head of State and Government.",
        },
        {
            "id": "ch_sst_fb_3",
            "question": "Democracy means 'rule by the people'.",
            "options": {"A": "True", "B": "False"},
            "correct_answer": "A",
            "question_type": "true-false",
            "explanation": "Democracy comes from Greek 'demos' (people) and 'kratos' (rule) — literally 'rule by the people'.",
        },
        {
            "id": "ch_sst_fb_4",
            "question": "What is the main cause of deforestation in Ghana?",
            "correct_answer": "Illegal logging and agriculture",
            "question_type": "short-answer",
            "explanation": "Illegal logging (galamsey) and expansion of agriculture (especially cocoa farming) are the primary causes of deforestation in Ghana.",
        },
        {
            "id": "ch_sst_fb_5",
            "question": "What is the main purpose of the United Nations?",
            "options": {"A": "To control global trade", "B": "To maintain international peace and security", "C": "To set education standards", "D": "To create world laws"},
            "correct_answer": "B",
            "question_type": "mcq",
            "explanation": "The UN's primary purpose is maintaining international peace and security.",
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
