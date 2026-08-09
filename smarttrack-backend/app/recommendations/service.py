"""Phase-attributed programme recommendations — learner-facing, university-neutral."""
from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assessment.models import BehavioralProfile, UserSkillEstimate
from app.phases.models import Phase, UserLevelProgress, UserSubjectPerformance
from app.phases.service import unlock_next_phase_after_recommendation
from app.psychometrics.models import PsychometricOption, UserPsychometricBankResponse
from app.recommendations.behavioural_match import build_behavioural_match
from app.recommendations.models import Recommendation
from app.recommendations.presentation import (
    build_psychometric_prose,
    sanitize_phase_suggestions,
)
from app.users.models import AcademicRecord, User

logger = logging.getLogger(__name__)


async def _load_user_grades(db: AsyncSession, user_id: uuid.UUID) -> list[dict[str, str]]:
    rows = (
        await db.execute(select(AcademicRecord).where(AcademicRecord.user_id == user_id))
    ).scalars().all()
    return [{"subject": r.subject, "grade": r.grade} for r in rows if r.subject and r.grade]


async def _phases_completed_count(db: AsyncSession, user_id: uuid.UUID) -> int:
    from app.phases.models import Level

    phases = (await db.execute(select(Phase).order_by(Phase.number))).scalars().all()
    if not phases:
        return 0
    level_prog = {
        p.level_id: p
        for p in (
            await db.execute(select(UserLevelProgress).where(UserLevelProgress.user_id == user_id))
        ).scalars().all()
    }
    done = 0
    for phase in phases:
        levels = (
            await db.execute(select(Level).where(Level.phase_id == phase.id))
        ).scalars().all()
        if not levels:
            continue
        if all(
            (level_prog.get(lv.id) and level_prog[lv.id].status == "completed")
            for lv in levels
        ):
            done += 1
    return done


async def collect_behavioural_inputs(
    db: AsyncSession,
    user: User,
) -> dict:
    """Gather cumulative Atlas signals for BPM (no WASSCE)."""
    user_id = user.id
    perfs = (
        await db.execute(
            select(UserSubjectPerformance).where(UserSubjectPerformance.user_id == user_id)
        )
    ).scalars().all()
    subject_accuracies = {
        str(p.subject): float(p.rolling_accuracy or 0.5) for p in perfs
    }
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

    # Merge BehavioralProfile rows (0–1 or scaled) into trait map for BPM
    bp_rows = (
        await db.execute(
            select(BehavioralProfile).where(BehavioralProfile.user_id == user_id)
        )
    ).scalars().all()
    behavioral_traits = {t.trait: float(t.value) for t in bp_rows}
    for k, v in trait_scores.items():
        behavioral_traits.setdefault(k, float(v))

    skills = (
        await db.execute(
            select(UserSkillEstimate).where(UserSkillEstimate.user_id == user_id)
        )
    ).scalars().all()
    skill_estimates = {s.domain: float(s.theta) for s in skills}

    profile = user.learner_profile if isinstance(user.learner_profile, dict) else {}
    completed_lessons = list(profile.get("completed_lessons") or [])

    from app.assessment.models import ChallengeSession

    session_count = int(
        (
            await db.execute(
                select(func.count())
                .select_from(ChallengeSession)
                .where(ChallengeSession.user_id == user_id)
            )
        ).scalar()
        or 0
    )

    phases_completed = await _phases_completed_count(db, user_id)

    return {
        "programme_affinity_scores": dict(programme_scores),
        "subject_accuracies": subject_accuracies,
        "strong_subjects": strong_subjects,
        "trait_scores": dict(trait_scores),
        "behavioral_traits": behavioral_traits,
        "skill_estimates": skill_estimates,
        "completed_lessons": completed_lessons,
        "phases_completed": phases_completed,
        "session_count": session_count,
        "psych_prose": build_psychometric_prose(trait_scores),
    }


async def generate_behavioural_recommendations(
    db: AsyncSession,
    user: User,
    *,
    limit: int = 8,
    phase_label: str | None = None,
) -> dict:
    """Public helper: BPM ranked programmes for generate API or phase cards."""
    inputs = await collect_behavioural_inputs(db, user)
    match = build_behavioural_match(
        programme_affinity_scores=inputs["programme_affinity_scores"],
        subject_accuracies=inputs["subject_accuracies"],
        behavioral_traits=inputs["behavioral_traits"],
        skill_estimates=inputs["skill_estimates"],
        completed_lessons=inputs["completed_lessons"],
        phases_completed=inputs["phases_completed"],
        session_count=inputs["session_count"],
        limit=limit,
    )
    strong = inputs["strong_subjects"]
    challenge_bit = (
        f" Your challenge work has been especially strong in {', '.join(strong)}."
        if strong
        else ""
    )
    phase_bit = f" after {phase_label}" if phase_label else ""
    summary = (
        f"{inputs['psych_prose']}{phase_bit}, Atlas ranked programmes from your "
        f"psychometric profile and learning activity in Atlas so far.{challenge_bit} "
        f"Upload WASSCE results later to refine these with admission cut-offs."
    )
    return {
        **match,
        "summary_message": summary,
        "inputs": inputs,
    }


async def generate_phase_recommendation(
    db: AsyncSession,
    user_id: uuid.UUID,
    phase_id: int,
) -> dict:
    phase = (await db.execute(select(Phase).where(Phase.id == phase_id))).scalar_one()
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()

    behavioural = await generate_behavioural_recommendations(
        db,
        user,
        limit=8,
        phase_label=phase.name,
    )
    suggestions = list(behavioural.get("programmes") or [])
    inputs = behavioural.get("inputs") or {}
    psych_prose = inputs.get("psych_prose") or ""
    strong_subjects = inputs.get("strong_subjects") or []
    challenge_bit = (
        f" Your challenge work has been especially strong in {', '.join(strong_subjects)}."
        if strong_subjects
        else ""
    )

    max_phase_row = (
        await db.execute(select(func.max(Phase.number)))
    ).scalar_one_or_none()
    max_phase_number = int(max_phase_row or phase.number)
    is_final = phase.number >= max_phase_number
    grades = await _load_user_grades(db, user_id)

    # Phase cards always store behavioural match. If this is the final phase and
    # grades already exist, append a short note that admission refine is available.
    if is_final:
        rationale = (
            f"{psych_prose} After completing {phase.name}, Atlas ranked programmes from "
            f"your full behavioural profile in Atlas so far.{challenge_bit} "
            f"You can optionally upload WASSCE or academic results to refine these "
            f"matches with aggregate and admission cut-offs."
        )
    else:
        rationale = (
            f"{psych_prose} After {phase.name}, Atlas ranked programmes from your "
            f"psychometric profile and challenge activity so far.{challenge_bit} "
            f"Recommendations will refine as you complete more phases."
        )

    if grades and is_final:
        rationale += (
            " Academic results are already on file — use Get Recommendations to see "
            "the WASSCE-refined admission view."
        )

    await db.execute(
        delete(Recommendation).where(
            Recommendation.user_id == user_id,
            Recommendation.phase_id == phase.id,
        )
    )

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
        "recommendation_kind": "behavioural_match",
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
    out.sort(key=lambda r: int(r.get("phase") or 0))
    return out


__all__ = [
    "generate_phase_recommendation",
    "generate_behavioural_recommendations",
    "list_recommendations",
    "collect_behavioural_inputs",
]
