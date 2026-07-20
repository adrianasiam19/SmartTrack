"""Generate mixed-subject challenge questions at a prescribed difficulty.

Primary source: DeepSeek LLM, constrained by phase curriculum scope.
Fallback: phase academic bank (SHS-tagged), then static MCQ.

Questions are random per call; callers pass exclude sets so nothing repeats
inside a single level session.
"""
from __future__ import annotations

import json
import logging
import random
import re
from typing import Any

import httpx

from app.config import settings
from app.phases.academic_bank import select_question as select_from_bank
from app.phases.adaptive import normalize_question_text

logger = logging.getLogger(__name__)

SUBJECT_LABELS = {
    "english": "English Language",
    "core_maths": "Core Mathematics",
    "integrated_science": "Integrated Science",
    "social_studies": "Social Studies",
}

PHASE_SCOPE: dict[int, str] = {
    1: (
        "Use ONLY Year 1 / SHS 1 curriculum topics for this subject. "
        "Do not include Year 2, Year 3, or WASSCE exam-style items."
    ),
    2: (
        "Use ONLY Year 1 or Year 2 / SHS 1–2 curriculum topics. "
        "Do not include Year 3-only or WASSCE exam-style items."
    ),
    3: (
        "You may use Year 1–3 / SHS 1–3 topics AND WASSCE-style application questions. "
        "Prefer exam-style reasoning when difficulty is high (10+)."
    ),
}


def _fallback_question(subject: str, effective_difficulty: int, salt: int = 0) -> dict[str, Any]:
    label = SUBJECT_LABELS.get(subject, subject)
    variants = [
        "Which approach best shows careful reasoning for this subject?",
        "What is the most reliable next step when solving a problem here?",
        "Which habit most improves accuracy in this subject?",
        "How should a careful student check their work?",
    ]
    return {
        "question_text": (
            f"[{label} · difficulty {effective_difficulty}] "
            f"{variants[salt % len(variants)]}"
        ),
        "question_type": "mcq",
        "options": {
            "A": "Skip the problem and guess",
            "B": "Break it into steps and check your work",
            "C": "Ignore instructions",
            "D": "Copy a random answer",
        },
        "correct_answer": "B",
        "explanation": "Careful step-by-step reasoning is the reliable approach.",
        "source": "fallback",
    }


def _pick_target_level(phase_number: int, effective_difficulty: int, rng: random.Random) -> str:
    if phase_number <= 1:
        return "SHS 1"
    if phase_number == 2:
        return rng.choice(["SHS 1", "SHS 2"])
    if effective_difficulty >= 10:
        return rng.choice(["SHS 3", "WASSCE"])
    return rng.choice(["SHS 1", "SHS 2", "SHS 3", "WASSCE"])


async def _llm_question(
    *,
    phase_number: int,
    level_number: int,
    subject: str,
    effective_difficulty: int,
    performance_summary: str,
    question_budget: int,
    exclude_texts: set[str],
    rng: random.Random,
) -> dict[str, Any] | None:
    if not settings.DEEPSEEK_API_KEY:
        return None

    label = SUBJECT_LABELS.get(subject, subject)
    scope = PHASE_SCOPE.get(phase_number, PHASE_SCOPE[1])
    target = _pick_target_level(phase_number, effective_difficulty, rng)
    style_line = (
        "Write a WASSCE-style application MCQ (original — do not copy past papers)."
        if target == "WASSCE"
        else f"Write a classroom MCQ at {target} curriculum depth."
    )
    avoid = ""
    if exclude_texts:
        samples = list(exclude_texts)[-24:]
        avoid = (
            "Do NOT repeat or paraphrase any of these already-used questions:\n- "
            + "\n- ".join(samples)
            + "\n"
        )

    # Map difficulty bands so the model can feel the step-ups clearly.
    if effective_difficulty <= 4:
        band = "introductory / scaffolded"
    elif effective_difficulty <= 8:
        band = "standard classroom challenge"
    elif effective_difficulty <= 11:
        band = "advanced multi-step"
    else:
        band = "exam-hard / stretch"

    prompt = (
        f"Generate ONE ORIGINAL random multiple-choice question for Ghana secondary {label}.\n"
        f"Phase {phase_number}, Level {level_number} of 10 "
        f"(this level has {question_budget} questions total — keep each item focused).\n"
        f"Novelty seed: {rng.randint(1, 10_000_000)}.\n"
        f"Hard constraint — curriculum scope: {scope}\n"
        f"This item target: {target}. {style_line}\n"
        f"Difficulty MUST match {effective_difficulty} on a 1–15 scale "
        f"({band}). Do not make it easier than requested.\n"
        f"Adaptive rule: subjects the learner answers correctly should get HARDER "
        f"over levels; subjects they miss keep the SAME difficulty — honour the "
        f"effective difficulty given above.\n"
        f"Learner recent performance: {performance_summary}\n"
        f"{avoid}"
        "Never reproduce copyrighted WAEC/WASSCE past-paper wording.\n"
        "Return ONLY JSON with keys: question_text, options (object A-D), "
        "correct_answer (letter), explanation, target_level "
        f"(use exactly \"{target}\")."
    )

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
                json={
                    "model": settings.DEEPSEEK_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You generate original, varied Ghana secondary-school MCQs. "
                                "Never repeat a question already listed. "
                                "Match the requested difficulty exactly. "
                                "Obey curriculum scope and the level question budget. "
                                "Reply with JSON only."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.9,
                },
            )
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"]
                parsed = _parse_json(content)
                if parsed and parsed.get("question_text") and parsed.get("correct_answer"):
                    text = str(parsed["question_text"]).strip()
                    if normalize_question_text(text) in exclude_texts:
                        return None
                    opts = parsed.get("options") or {}
                    if isinstance(opts, list):
                        opts = {chr(65 + i): str(o) for i, o in enumerate(opts[:4])}
                    return {
                        "question_text": text,
                        "question_type": "mcq",
                        "options": opts,
                        "correct_answer": str(parsed["correct_answer"]).strip().upper()[:1],
                        "explanation": parsed.get("explanation"),
                        "target_level": parsed.get("target_level") or target,
                        "source": "llm",
                    }
            else:
                logger.warning("DeepSeek question gen HTTP %s", res.status_code)
    except Exception as exc:
        logger.warning("DeepSeek question gen failed: %s", exc)
    return None


async def generate_subject_question(
    *,
    phase_number: int,
    level_number: int,
    subject: str,
    effective_difficulty: int,
    performance_summary: str,
    exclude_bank_ids: set[str] | None = None,
    exclude_texts: set[str] | None = None,
    question_budget: int | None = None,
    rng: random.Random | None = None,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """LLM-first with retries to avoid duplicates; bank then fallback."""
    rng = rng or random.Random()
    used_ids = exclude_bank_ids or set()
    used_texts = set(exclude_texts or set())
    budget = question_budget if question_budget is not None else 10

    for _attempt in range(max_attempts):
        llm = await _llm_question(
            phase_number=phase_number,
            level_number=level_number,
            subject=subject,
            effective_difficulty=effective_difficulty,
            performance_summary=performance_summary,
            question_budget=budget,
            exclude_texts=used_texts,
            rng=rng,
        )
        if llm:
            return llm

    from_bank = select_from_bank(
        phase_number=phase_number,
        subject=subject,
        effective_difficulty=effective_difficulty,
        exclude_ids=used_ids,
        rng=rng,
    )
    if from_bank:
        norm = normalize_question_text(from_bank["question_text"])
        if norm not in used_texts:
            from_bank["source"] = "bank"
            return from_bank

    # Last resort: unique-ish static fallback
    for salt in range(8):
        fallback = _fallback_question(subject, effective_difficulty, salt=salt + rng.randint(0, 50))
        if normalize_question_text(fallback["question_text"]) not in used_texts:
            return fallback
    return _fallback_question(subject, effective_difficulty, salt=rng.randint(0, 999))


def _parse_json(content: str) -> dict[str, Any] | None:
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", content, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None
