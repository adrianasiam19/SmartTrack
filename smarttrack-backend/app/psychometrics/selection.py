"""Deterministic psychometric checkpoint selection."""
from __future__ import annotations

import uuid
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.psychometrics.models import (
    PsychometricOption,
    PsychometricQuestion,
    UserPsychometricBankResponse,
)


async def select_checkpoint_questions(
    db: AsyncSession,
    user_id: uuid.UUID,
    phase_id: int,
) -> list[PsychometricQuestion]:
    count = settings.PSYCHO_CHECKPOINT_COUNT
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

    answered_ids = {h.question_id for h in history}
    # Exclude current + immediately preceding phase answers preferentially
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
    for q in all_q:
        by_category[q.category].append(q)

    selected: list[PsychometricQuestion] = []
    selected_ids: set[int] = set()
    categories = list(by_category.keys())

    # Round-robin across categories for spread
    while len(selected) < count:
        progressed = False
        for cat in categories:
            if len(selected) >= count:
                break
            candidates = [
                q
                for q in by_category[cat]
                if q.id not in selected_ids and q.id not in recent_q_ids
            ]
            if not candidates:
                candidates = [
                    q for q in by_category[cat] if q.id not in selected_ids and q.id not in answered_ids
                ]
            if not candidates:
                candidates = [q for q in by_category[cat] if q.id not in selected_ids]
            if not candidates:
                continue
            pick = candidates[0]
            selected.append(pick)
            selected_ids.add(pick.id)
            progressed = True
        if not progressed:
            break

    return selected


async def save_checkpoint_response(
    db: AsyncSession,
    user_id: uuid.UUID,
    phase_id: int,
    question_id: int,
    option_id: int,
) -> UserPsychometricBankResponse:
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
