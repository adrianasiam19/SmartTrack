"""Phase-attributed programme recommendations."""
from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.phases.models import Phase, UserSubjectPerformance
from app.phases.service import unlock_next_phase_after_recommendation
from app.psychometrics.models import PsychometricOption, UserPsychometricBankResponse
from app.recommendations.models import Recommendation


async def generate_phase_recommendation(
    db: AsyncSession,
    user_id: uuid.UUID,
    phase_id: int,
) -> dict:
    phase = (await db.execute(select(Phase).where(Phase.id == phase_id))).scalar_one()

    # Academic aggregates
    perfs = (
        await db.execute(
            select(UserSubjectPerformance).where(UserSubjectPerformance.user_id == user_id)
        )
    ).scalars().all()
    academic_bits = [
        f"{p.subject.replace('_', ' ')} accuracy {p.rolling_accuracy:.0%}"
        for p in perfs
    ]

    # Psychometric tag aggregation across all checkpoints
    responses = (
        await db.execute(
            select(UserPsychometricBankResponse)
            .where(UserPsychometricBankResponse.user_id == user_id)
            .options()
        )
    ).scalars().all()
    option_ids = [r.option_id for r in responses]
    programme_scores: dict[str, float] = defaultdict(float)
    trait_scores: dict[str, float] = defaultdict(float)

    if option_ids:
        options = (
            await db.execute(
                select(PsychometricOption).where(PsychometricOption.id.in_(option_ids))
            )
        ).scalars().all()
        for opt in options:
            for tag in opt.trait_tags or []:
                trait_scores[str(tag)] += 1
            for aff in opt.programme_affinity_tags or []:
                if isinstance(aff, dict) and aff.get("programme"):
                    programme_scores[aff["programme"]] += float(aff.get("weight", 0.5))

    ranked = sorted(programme_scores.items(), key=lambda x: x[1], reverse=True)
    suggestions = [
        {
            "programme": name.replace("_", " ").title(),
            "score": round(score, 3),
            "key": name,
        }
        for name, score in ranked[:5]
    ]
    if not suggestions:
        suggestions = [
            {"programme": "General Science", "score": 0.5, "key": "natural_sciences"},
            {"programme": "Business Studies", "score": 0.4, "key": "business_law"},
        ]

    top_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    rationale = (
        f"This recommendation reflects your progress through {phase.name}. "
        f"Academic signals: {'; '.join(academic_bits) if academic_bits else 'building profile'}. "
        f"Trait emphasis: {', '.join(t for t, _ in top_traits) if top_traits else 'still learning about you'}."
    )

    is_final = phase.number == 3
    row = Recommendation(
        user_id=user_id,
        phase_id=phase.id,
        generated_at=datetime.now(timezone.utc),
        programme_suggestions=suggestions,
        rationale_summary=rationale,
        is_final=is_final,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)

    await unlock_next_phase_after_recommendation(db, user_id, phase.id)

    return {
        "id": row.id,
        "phase": phase.number,
        "phase_label": phase.name,
        "generated_at": row.generated_at.isoformat(),
        "programme_suggestions": suggestions,
        "rationale_summary": rationale,
        "is_final": is_final,
    }


async def list_recommendations(db: AsyncSession, user_id: uuid.UUID) -> list[dict]:
    rows = (
        await db.execute(
            select(Recommendation, Phase)
            .join(Phase, Recommendation.phase_id == Phase.id)
            .where(Recommendation.user_id == user_id)
            .order_by(Recommendation.generated_at.desc())
        )
    ).all()
    out = []
    for rec, phase in rows:
        out.append(
            {
                "id": rec.id,
                "phase": phase.number,
                "phase_label": phase.name,
                "generated_at": rec.generated_at.isoformat(),
                "programme_suggestions": rec.programme_suggestions,
                "rationale_summary": rec.rationale_summary,
                "is_final": rec.is_final,
            }
        )
    return out
