"""Phase-attributed programme recommendations — KNUST cut-offs + grades only."""
from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.phases.models import Phase, UserSubjectPerformance
from app.phases.service import unlock_next_phase_after_recommendation
from app.psychometrics.models import PsychometricOption, UserPsychometricBankResponse
from app.recommendations.cutoffs import apply_cutoff_boundaries
from app.recommendations.models import Recommendation
from app.users.models import AcademicRecord

# Psych affinity keys → KNUST document families (soft ranking only)
AFFINITY_TO_FAMILY = {
    "engineering": "Engineering",
    "medicine_health": "Health Sciences",
    "health": "Health Sciences",
    "natural_sciences": "Natural Sciences",
    "science": "Natural Sciences",
    "computing": "Natural Sciences",
    "computing_it": "Natural Sciences",
}


def _family_fit_from_psych(programme_scores: dict[str, float]) -> dict[str, int]:
    families: dict[str, float] = defaultdict(float)
    for key, score in programme_scores.items():
        family = AFFINITY_TO_FAMILY.get(key.lower().replace(" ", "_"))
        if family:
            families[family] += float(score)
    if not families:
        return {
            "Health Sciences": 50,
            "Engineering": 50,
            "Natural Sciences": 50,
        }
    max_s = max(families.values()) or 1
    return {k: int((v / max_s) * 100) for k, v in families.items()}


async def _load_user_grades(db: AsyncSession, user_id: uuid.UUID) -> list[dict[str, str]]:
    rows = (
        await db.execute(select(AcademicRecord).where(AcademicRecord.user_id == user_id))
    ).scalars().all()
    return [{"subject": r.subject, "grade": r.grade} for r in rows if r.subject and r.grade]


async def generate_phase_recommendation(
    db: AsyncSession,
    user_id: uuid.UUID,
    phase_id: int,
) -> dict:
    phase = (await db.execute(select(Phase).where(Phase.id == phase_id))).scalar_one()

    perfs = (
        await db.execute(
            select(UserSubjectPerformance).where(UserSubjectPerformance.user_id == user_id)
        )
    ).scalars().all()
    academic_bits = [
        f"{p.subject.replace('_', ' ')} accuracy {p.rolling_accuracy:.0%}"
        for p in perfs
    ]

    responses = (
        await db.execute(
            select(UserPsychometricBankResponse).where(
                UserPsychometricBankResponse.user_id == user_id
            )
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

    grades = await _load_user_grades(db, user_id)
    family_fit = _family_fit_from_psych(programme_scores)
    top_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)[:5]

    suggestions: list[dict] = []
    if grades:
        knust = apply_cutoff_boundaries(
            grades=grades,
            family_fit_scores=family_fit,
            limit_per_band=8,
        )
        agg = knust.get("aggregate") or {}
        for band_key in ("eligible", "stretch"):
            for item in (knust.get("bands") or {}).get(band_key) or []:
                suggestions.append(
                    {
                        "programme": item["programme"],
                        "score": round(float(item.get("family_fit_score") or 0) / 100.0, 3),
                        "key": item["programme"],
                        "family": item.get("family"),
                        "cutoff": item.get("cutoff"),
                        "eligibility_band": band_key,
                        "university": "KNUST",
                        "source": "knust_cutoffs",
                    }
                )
        if agg.get("aggregate") is not None:
            rationale = (
                f"After {phase.name}, your WASSCE aggregate ({agg['aggregate']}) was matched "
                f"only to programmes in the KNUST Science / Engineering / Health cut-off list. "
                f"Academic signals: {'; '.join(academic_bits) if academic_bits else 'building profile'}. "
                f"Trait emphasis: {', '.join(t for t, _ in top_traits) if top_traits else 'still learning about you'}."
            )
        else:
            rationale = (
                f"After {phase.name}, Atlas could not compute a reliable WASSCE aggregate from "
                f"your uploaded grades, so no KNUST programmes were suggested. "
                f"Re-upload clearer results on the Recommendations page."
            )
            suggestions = []
    else:
        rationale = (
            f"After {phase.name}, upload your WASSCE results to receive KNUST programme "
            f"matches from the official Science / Engineering / Health cut-off document. "
            f"Atlas does not invent general programmes without grades. "
            f"Trait emphasis so far: {', '.join(t for t, _ in top_traits) if top_traits else 'still learning about you'}."
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
