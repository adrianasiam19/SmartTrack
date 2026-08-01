"""Phase-attributed programme recommendations — learner-facing, university-neutral."""
from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.phases.models import Phase, UserSubjectPerformance
from app.phases.service import unlock_next_phase_after_recommendation
from app.psychometrics.models import PsychometricOption, UserPsychometricBankResponse
from app.recommendations.cutoffs import apply_cutoff_boundaries
from app.recommendations.ml_career import generate_ml_knust_alternate
from app.recommendations.models import Recommendation
from app.recommendations.presentation import (
    build_psychometric_prose,
    sanitize_phase_suggestions,
    select_suitable_and_competitive,
)
from app.users.models import AcademicRecord

logger = logging.getLogger(__name__)

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
    strong_subjects = [
        p.subject.replace("_", " ")
        for p in perfs
        if float(p.rolling_accuracy or 0) >= 0.6
    ][:3]

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
    psych_prose = build_psychometric_prose(trait_scores)

    suggestions: list[dict] = []
    if grades:
        selected = select_suitable_and_competitive(
            grades=grades,
            family_fit_scores=family_fit,
            limit=6,
        )
        agg = (selected.get("aggregate") or {}).get("aggregate")
        # ML Decision Tree is primary; cut-off list is silent fallback.
        knust_payload = apply_cutoff_boundaries(
            grades=grades,
            family_fit_scores=family_fit,
            limit_per_band=50,
        )
        trait_floats = {k: float(v) for k, v in trait_scores.items()}
        ml = generate_ml_knust_alternate(
            academic_grades=grades,
            behavioral_traits=trait_floats,
            skill_estimates={},
            knust_payload=knust_payload,
        )
        if ml.get("enabled") and ml.get("programmes"):
            suggestions = list(ml.get("programmes") or [])[:6]
        else:
            suggestions = selected.get("suitable") or []

        if agg is not None:
            challenge_bit = (
                f" Your challenge work has been especially strong in {', '.join(strong_subjects)}."
                if strong_subjects
                else ""
            )
            rationale = (
                f"{psych_prose} After {phase.name}, Atlas combined your psychometric profile"
                f"{challenge_bit} with your estimated aggregate of {agg} to suggest suitable "
                f"programmes near your results."
            )
        else:
            rationale = (
                f"{psych_prose} Atlas could not yet compute a reliable aggregate from your "
                f"uploaded results. Re-upload a clearer results slip on the Recommendations page."
            )
            suggestions = []
    else:
        rationale = (
            f"{psych_prose} Upload your WASSCE results on the Recommendations page so Atlas "
            f"can match programmes to both your profile and your aggregate."
        )

    # Replace prior rows for this phase so history does not duplicate Phase cards.
    await db.execute(
        delete(Recommendation).where(
            Recommendation.user_id == user_id,
            Recommendation.phase_id == phase.id,
        )
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

    try:
        from app.notifications.events import notify_recommendation_ready

        await notify_recommendation_ready(
            db,
            user_id,
            phase_number=phase.number,
            is_final=is_final,
        )
        await db.commit()
    except Exception:
        logger.exception("Failed to create recommendation notification")

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
    """Return latest recommendation per phase only (no duplicate Phase cards)."""
    rows = (
        await db.execute(
            select(Recommendation, Phase)
            .join(Phase, Recommendation.phase_id == Phase.id)
            .where(Recommendation.user_id == user_id)
            .order_by(Recommendation.generated_at.desc())
        )
    ).all()

    seen_phases: set[int] = set()
    out: list[dict] = []
    for rec, phase in rows:
        if phase.id in seen_phases:
            continue
        seen_phases.add(phase.id)
        out.append(
            {
                "id": rec.id,
                "phase": phase.number,
                "phase_label": phase.name,
                "generated_at": rec.generated_at.isoformat(),
                "programme_suggestions": sanitize_phase_suggestions(
                    rec.programme_suggestions
                ),
                "rationale_summary": rec.rationale_summary,
                "is_final": rec.is_final,
            }
        )
    # Show Phase 1 → 2 → 3 for a natural story
    out.sort(key=lambda r: int(r.get("phase") or 0))
    return out
