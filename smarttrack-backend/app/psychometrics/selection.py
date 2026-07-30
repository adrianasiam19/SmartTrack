"""Post-phase psychometric checkpoint selection.

After each phase's 10 levels, Atlas asks a short Get-to-Know-You set:
exactly one question from each of N distinct tagged categories (default 8).

The LLM intelligently chooses which categories and bank questions to use for
this learner and phase (varied coverage for ML). A deterministic heuristic
is the fallback when the model is unavailable.
"""
from __future__ import annotations

import hashlib
import json
import logging
import random
import re
import uuid
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.phases.models import Phase
from app.psychometrics.models import (
    PsychometricQuestion,
    UserPsychometricBankResponse,
)
from app.users.models import User

logger = logging.getLogger(__name__)

# Full tagged bank — checkpoints sample a subset each phase.
CHECKPOINT_CATEGORIES: list[str] = [
    "Learning Preferences",
    "Study Habits",
    "Problem-Solving Style",
    "Curiosity",
    "Creativity",
    "Leadership",
    "Teamwork",
    "Persistence",
    "Motivation",
    "Career Interests",
    "Decision Making",
    "Communication",
    "Time Management",
    "Confidence",
    "Academic Interests",
    "Technology Interest",
    "Engineering Interest",
    "Medical and Health Interest",
    "Environmental Interest",
    "Research Interest",
]

CHECKPOINT_SYSTEM_PROMPT = (
    "You are Atlas, selecting Get-to-Know-You psychometric questions for an SHS "
    "learner in Ghana after they finish a challenge phase. "
    "You must only choose from the provided bank candidates. "
    "Vary coverage thoughtfully for ML profiling — never invent questions."
)


def _phase_rng(user_id: uuid.UUID, phase_id: int) -> random.Random:
    """Stable per-user/phase RNG so the same session is consistent, but users differ."""
    seed_material = f"{user_id}:{phase_id}:psycho-checkpoint".encode()
    seed = int(hashlib.sha256(seed_material).hexdigest()[:16], 16)
    return random.Random(seed)


def _pick_categories_for_checkpoint(
    *,
    available: list[str],
    covered_before: set[str],
    count: int,
    rng: random.Random,
) -> list[str]:
    """Prefer categories this user has not covered yet; fill randomly if needed."""
    if not available:
        return []
    target = min(count, len(available))
    fresh = [c for c in available if c not in covered_before]
    reused = [c for c in available if c in covered_before]
    rng.shuffle(fresh)
    rng.shuffle(reused)
    chosen = (fresh + reused)[:target]
    rng.shuffle(chosen)
    return chosen


def _eligible_pool(
    pool: list[PsychometricQuestion],
    *,
    selected_ids: set[int],
    recent_q_ids: set[int],
    answered_ids: set[int],
) -> list[PsychometricQuestion]:
    candidates = [
        q for q in pool if q.id not in selected_ids and q.id not in recent_q_ids
    ]
    if not candidates:
        candidates = [
            q
            for q in pool
            if q.id not in selected_ids and q.id not in answered_ids
        ]
    if not candidates:
        candidates = [q for q in pool if q.id not in selected_ids]
    return candidates


def _heuristic_select(
    *,
    by_category: dict[str, list[PsychometricQuestion]],
    available: list[str],
    covered_before: set[str],
    count: int,
    rng: random.Random,
    recent_q_ids: set[int],
    answered_ids: set[int],
) -> list[PsychometricQuestion]:
    chosen_categories = _pick_categories_for_checkpoint(
        available=available,
        covered_before=covered_before,
        count=count,
        rng=rng,
    )
    selected: list[PsychometricQuestion] = []
    selected_ids: set[int] = set()
    for cat in chosen_categories:
        candidates = _eligible_pool(
            by_category[cat],
            selected_ids=selected_ids,
            recent_q_ids=recent_q_ids,
            answered_ids=answered_ids,
        )
        if not candidates:
            continue
        pick = rng.choice(candidates)
        selected.append(pick)
        selected_ids.add(pick.id)
    return selected


def _parse_bank_id_list(raw: str) -> list[str]:
    """Extract a JSON array of bank_id strings from an LLM response."""
    text = (raw or "").strip()
    if not text:
        return []
    # Prefer fenced / raw JSON array
    match = re.search(r"\[[\s\S]*?\]", text)
    if not match:
        return []
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    out: list[str] = []
    for item in parsed:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
        elif isinstance(item, dict):
            bank_id = item.get("bank_id") or item.get("id")
            if isinstance(bank_id, str) and bank_id.strip():
                out.append(bank_id.strip())
    return out


def _build_llm_candidate_prompt(
    *,
    count: int,
    phase_number: int | None,
    phase_name: str | None,
    programme: str | None,
    shs_level: str | None,
    covered_before: set[str],
    candidates: list[dict],
) -> str:
    covered = ", ".join(sorted(covered_before)) or "none yet"
    lines = "\n".join(
        f'- bank_id="{c["bank_id"]}" | category="{c["category"]}" | {c["text"]}'
        for c in candidates
    )
    return f"""
Select exactly {count} psychometric questions for this learner's phase checkpoint.

LEARNER / PHASE CONTEXT
- SHS level: {shs_level or "unknown"}
- Programme: {programme or "unknown"}
- Phase: {phase_number or "?"} — {phase_name or "Challenge phase"}
- Categories already covered in earlier phases: {covered}

GOAL
- Build a balanced Get-to-Know-You profile for ML recommendations.
- Prefer categories NOT yet covered when possible.
- Mix soft-skill and interest categories thoughtfully for THIS learner.
- Vary selections so different learners and phases do not look identical.
- Choose exactly one question per category (no duplicate categories).
- Choose ONLY from the candidate list below — do not invent bank_ids.

CANDIDATES
{lines}

Return ONLY a JSON array of exactly {count} bank_id strings, e.g.
["qb-001", "qb-040", "qb-090"]
""".strip()


async def _llm_select_bank_ids(
    *,
    count: int,
    phase_number: int | None,
    phase_name: str | None,
    programme: str | None,
    shs_level: str | None,
    covered_before: set[str],
    candidates: list[dict],
) -> list[str]:
    if not candidates:
        return []
    from app.assessment.starter_arena import get_ai_response

    prompt = _build_llm_candidate_prompt(
        count=count,
        phase_number=phase_number,
        phase_name=phase_name,
        programme=programme,
        shs_level=shs_level,
        covered_before=covered_before,
        candidates=candidates,
    )
    raw = await get_ai_response(
        [
            {"role": "system", "content": CHECKPOINT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )
    if not raw:
        return []
    return _parse_bank_id_list(raw)


def _hydrate_llm_picks(
    bank_ids: list[str],
    *,
    by_bank_id: dict[str, PsychometricQuestion],
    count: int,
) -> list[PsychometricQuestion]:
    selected: list[PsychometricQuestion] = []
    seen_categories: set[str] = set()
    for bank_id in bank_ids:
        question = by_bank_id.get(bank_id)
        if not question:
            continue
        if question.category in seen_categories:
            continue
        selected.append(question)
        seen_categories.add(question.category)
        if len(selected) >= count:
            break
    return selected


async def select_checkpoint_questions(
    db: AsyncSession,
    user_id: uuid.UUID,
    phase_id: int,
) -> list[PsychometricQuestion]:
    """
    Pick one question from each of PSYCHO_CHECKPOINT_COUNT distinct categories.

    Primary path: LLM chooses a varied mix from eligible bank candidates.
    Fallback: deterministic per-user/phase heuristic.
    """
    count = max(1, int(settings.PSYCHO_CHECKPOINT_COUNT))
    rng = _phase_rng(user_id, phase_id)

    all_q = (
        await db.execute(
            select(PsychometricQuestion)
            .options(selectinload(PsychometricQuestion.options))
            .order_by(PsychometricQuestion.number)
        )
    ).scalars().all()

    history = (
        await db.execute(
            select(UserPsychometricBankResponse).where(
                UserPsychometricBankResponse.user_id == user_id
            )
        )
    ).scalars().all()

    phase = (
        await db.execute(select(Phase).where(Phase.id == phase_id))
    ).scalar_one_or_none()
    user = (
        await db.execute(select(User).where(User.id == user_id))
    ).scalar_one_or_none()

    answered_ids = {h.question_id for h in history}
    recent_phase_ids = {phase_id}
    phases_answered = {h.phase_id for h in history if h.phase_id is not None}
    if phases_answered:
        prev = max((p for p in phases_answered if p < phase_id), default=None)
        if prev is not None:
            recent_phase_ids.add(prev)
    recent_q_ids = {
        h.question_id for h in history if h.phase_id in recent_phase_ids
    }

    by_category: dict[str, list[PsychometricQuestion]] = defaultdict(list)
    id_to_category = {}
    by_bank_id: dict[str, PsychometricQuestion] = {}
    for q in all_q:
        by_category[q.category].append(q)
        id_to_category[q.id] = q.category
        by_bank_id[q.bank_id] = q

    covered_before = {
        id_to_category[h.question_id]
        for h in history
        if h.phase_id is not None
        and h.phase_id != phase_id
        and h.question_id in id_to_category
    }

    available = [c for c in CHECKPOINT_CATEGORIES if c in by_category]
    for cat in sorted(by_category.keys()):
        if cat not in available:
            available.append(cat)

    # Build a compact candidate shortlist for the LLM (up to 3 per category).
    llm_candidates: list[dict] = []
    for cat in available:
        pool = _eligible_pool(
            by_category[cat],
            selected_ids=set(),
            recent_q_ids=recent_q_ids,
            answered_ids=answered_ids,
        )
        rng.shuffle(pool)
        for question in pool[:3]:
            llm_candidates.append(
                {
                    "bank_id": question.bank_id,
                    "category": question.category,
                    "text": question.text[:160],
                }
            )

    selected: list[PsychometricQuestion] = []
    try:
        bank_ids = await _llm_select_bank_ids(
            count=count,
            phase_number=phase.number if phase else None,
            phase_name=phase.name if phase else None,
            programme=user.programme if user else None,
            shs_level=user.shs_level if user else None,
            covered_before=covered_before,
            candidates=llm_candidates,
        )
        selected = _hydrate_llm_picks(bank_ids, by_bank_id=by_bank_id, count=count)
        if len(selected) < count:
            logger.info(
                "LLM checkpoint returned %s/%s valid picks; filling heuristically",
                len(selected),
                count,
            )
    except Exception as exc:
        logger.warning("LLM checkpoint selection failed: %s", exc)
        selected = []

    if len(selected) >= count:
        return selected[:count]

    # Fill / replace with heuristic so we always return a full varied set.
    already_cats = {q.category for q in selected}
    fill = _heuristic_select(
        by_category=by_category,
        available=[c for c in available if c not in already_cats],
        covered_before=covered_before,
        count=count - len(selected),
        rng=rng,
        recent_q_ids=recent_q_ids,
        answered_ids=answered_ids,
    )
    selected.extend(fill)

    if len(selected) < count:
        # Absolute fallback: ignore prior category filter.
        more = _heuristic_select(
            by_category=by_category,
            available=available,
            covered_before=covered_before,
            count=count,
            rng=rng,
            recent_q_ids=recent_q_ids,
            answered_ids=answered_ids,
        )
        seen = {q.id for q in selected}
        for q in more:
            if q.id in seen or q.category in {x.category for x in selected}:
                continue
            selected.append(q)
            if len(selected) >= count:
                break

    return selected[:count]


async def save_checkpoint_response(
    db: AsyncSession,
    user_id: uuid.UUID,
    phase_id: int,
    question_id: int,
    option_id: int,
) -> UserPsychometricBankResponse:
    existing = (
        await db.execute(
            select(UserPsychometricBankResponse).where(
                UserPsychometricBankResponse.user_id == user_id,
                UserPsychometricBankResponse.question_id == question_id,
                UserPsychometricBankResponse.phase_id == phase_id,
            )
        )
    ).scalar_one_or_none()
    if existing:
        existing.option_id = option_id
        await db.commit()
        await db.refresh(existing)
        return existing

    row = UserPsychometricBankResponse(
        user_id=user_id,
        question_id=question_id,
        option_id=option_id,
        phase_id=phase_id,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row
