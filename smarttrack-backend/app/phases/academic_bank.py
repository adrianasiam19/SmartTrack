"""Phase academic question bank — load + select by phase rules."""
from __future__ import annotations

import json
import logging
import random
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_BANK_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "phase_academic_bank.json"

# Internal SHS tags (never shown in UI as SHS labels)
PHASE_SHS_LEVELS: dict[int, set[str]] = {
    1: {"SHS 1"},
    2: {"SHS 1", "SHS 2"},
    3: {"SHS 1", "SHS 2", "SHS 3"},
}


@lru_cache(maxsize=1)
def load_bank() -> list[dict[str, Any]]:
    if not _BANK_PATH.exists():
        logger.warning("Phase academic bank missing at %s", _BANK_PATH)
        return []
    raw = json.loads(_BANK_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        return []
    return [q for q in raw if isinstance(q, dict) and q.get("question_text") and q.get("correct_answer")]


def allowed_levels_for_phase(phase_number: int) -> set[str]:
    return PHASE_SHS_LEVELS.get(phase_number, PHASE_SHS_LEVELS[1])


def include_wassce_for_phase(phase_number: int) -> bool:
    return phase_number >= 3


def _eligible(
    phase_number: int,
    subject: str,
    exclude_ids: set[str],
) -> list[dict[str, Any]]:
    levels = allowed_levels_for_phase(phase_number)
    allow_wassce = include_wassce_for_phase(phase_number)
    out: list[dict[str, Any]] = []
    for q in load_bank():
        qid = str(q.get("id") or "")
        if qid and qid in exclude_ids:
            continue
        if q.get("subject") != subject:
            continue
        style = (q.get("exam_style") or "classroom").lower()
        if style == "wassce":
            if allow_wassce:
                out.append(q)
            continue
        if q.get("shs_level") in levels:
            out.append(q)
    return out


def select_question(
    *,
    phase_number: int,
    subject: str,
    effective_difficulty: int,
    exclude_ids: set[str] | None = None,
    rng: random.Random | None = None,
) -> dict[str, Any] | None:
    """
    Pick one bank question for subject, filtered by phase rules.
    Prefers items near effective_difficulty. Returns None if pool empty.
    """
    exclude = exclude_ids or set()
    pool = _eligible(phase_number, subject, exclude)
    if not pool:
        return None

    rng = rng or random.Random()
    # Score by closeness to target difficulty, then sample among best band
    scored: list[tuple[int, dict[str, Any]]] = []
    for q in pool:
        diff = int(q.get("difficulty") or 5)
        scored.append((abs(diff - effective_difficulty), q))
    scored.sort(key=lambda t: t[0])
    best_delta = scored[0][0]
    # Keep items within +2 of best distance so sessions vary
    band = [q for d, q in scored if d <= best_delta + 2]
    chosen = rng.choice(band)

    opts = chosen.get("options") or {}
    if isinstance(opts, list):
        opts = {chr(65 + i): str(o) for i, o in enumerate(opts[:4])}

    return {
        "bank_id": chosen.get("id"),
        "question_text": chosen["question_text"],
        "question_type": "mcq",
        "options": opts,
        "correct_answer": str(chosen["correct_answer"]).strip().upper()[:1],
        "explanation": chosen.get("explanation"),
        "difficulty": int(chosen.get("difficulty") or effective_difficulty),
        "shs_level": chosen.get("shs_level"),
        "exam_style": chosen.get("exam_style"),
    }


def bank_stats() -> dict[str, Any]:
    items = load_bank()
    by_level: dict[str, int] = {}
    by_subject: dict[str, int] = {}
    wassce = 0
    for q in items:
        by_level[str(q.get("shs_level"))] = by_level.get(str(q.get("shs_level")), 0) + 1
        by_subject[str(q.get("subject"))] = by_subject.get(str(q.get("subject")), 0) + 1
        if (q.get("exam_style") or "").lower() == "wassce":
            wassce += 1
    return {"total": len(items), "by_level": by_level, "by_subject": by_subject, "wassce": wassce}
