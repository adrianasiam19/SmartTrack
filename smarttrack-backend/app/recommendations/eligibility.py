"""
Recommendation eligibility — unlock programme generate after meaningful phase progress.

Mandatory: every level in at least one phase is completed.
Recommended (soft): at least one Learning Center lesson completed (encouraged, not blocking).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.phases.models import Phase, UserLevelProgress
from app.phases.service import ensure_user_progression
from app.users.models import User

FRIENDLY_BLOCKED_TITLE = "You are not yet eligible for a recommendation."

FRIENDLY_BLOCKED_MESSAGE = (
    "You are making great progress!\n\n"
    "Complete the remaining levels in this phase to unlock your personalised "
    "programme recommendations.\n\n"
    "We also recommend exploring at least one lesson in the Learning Center to "
    "strengthen your learner profile and improve future recommendations."
)

FRIENDLY_BLOCKED_SHORT = (
    "Please complete all levels in this phase before requesting your "
    "personalised programme recommendations."
)


async def evaluate_recommendation_eligibility(
    db: AsyncSession,
    user: User,
) -> dict[str, Any]:
    """
    Returns eligibility payload for UI + generate gate.

    eligible (bool): mandatory phase-level requirement met
    learning_recommended_done (bool): soft Learning Center nudge
    """
    await ensure_user_progression(db, user.id)

    phases = (
        await db.execute(select(Phase).options(selectinload(Phase.levels)).order_by(Phase.number))
    ).scalars().all()
    level_prog = {
        p.level_id: p
        for p in (
            await db.execute(select(UserLevelProgress).where(UserLevelProgress.user_id == user.id))
        ).scalars().all()
    }

    phase_summaries: list[dict[str, Any]] = []
    phases_with_all_levels_done: list[int] = []
    current_incomplete: dict[str, Any] | None = None

    for phase in phases:
        levels = sorted(phase.levels, key=lambda L: L.number)
        if not levels:
            continue
        statuses = []
        completed = 0
        for level in levels:
            lp = level_prog.get(level.id)
            st = lp.status if lp else "locked"
            statuses.append(st)
            if st == "completed":
                completed += 1
        total = len(levels)
        all_done = completed == total and total > 0
        summary = {
            "phase_number": phase.number,
            "phase_name": phase.name,
            "levels_completed": completed,
            "levels_total": total,
            "all_levels_completed": all_done,
        }
        phase_summaries.append(summary)
        if all_done:
            phases_with_all_levels_done.append(phase.number)
        elif current_incomplete is None and completed > 0:
            current_incomplete = summary
        elif current_incomplete is None and any(s != "locked" for s in statuses):
            current_incomplete = summary

    # If nothing started, treat Phase 1 as the focus
    if current_incomplete is None and phase_summaries:
        current_incomplete = next(
            (p for p in phase_summaries if not p["all_levels_completed"]),
            phase_summaries[0],
        )

    profile = user.learner_profile if isinstance(user.learner_profile, dict) else {}
    completed_lessons = list(profile.get("completed_lessons") or [])
    learning_done = len(completed_lessons) >= 1

    eligible = len(phases_with_all_levels_done) > 0
    remaining = 0
    focus_phase = None
    if current_incomplete:
        remaining = max(
            0,
            int(current_incomplete["levels_total"]) - int(current_incomplete["levels_completed"]),
        )
        focus_phase = {
            "number": current_incomplete["phase_number"],
            "name": current_incomplete["phase_name"],
            "levels_completed": current_incomplete["levels_completed"],
            "levels_total": current_incomplete["levels_total"],
            "levels_remaining": remaining,
        }

    all_phases_completed = (
        len(phases_with_all_levels_done) >= len(phase_summaries) and len(phase_summaries) > 0
    )
    wassce_on_file = False
    upload = profile.get("academic_upload") if isinstance(profile, dict) else None
    if isinstance(upload, dict) and upload.get("confirmed") is not False:
        if upload.get("filename") or upload.get("grades"):
            wassce_on_file = True

    if eligible:
        if all_phases_completed:
            title = "Learning journey complete"
            message = (
                "You have completed all challenge phases. Atlas can already recommend "
                "programmes from your psychometric profile and challenge activity.\n\n"
                "Optional next step: upload WASSCE or academic results so Atlas can tweak "
                "those matches with your aggregate and admission cut-offs."
            )
        else:
            title = "Recommendations unlocked"
            message = (
                "You have unlocked programme recommendations by completing all levels "
                "in at least one phase. Tap Get Recommendations to see matches based on "
                "your Atlas activity so far — WASSCE upload is not required yet."
            )
        if not learning_done:
            message += (
                " Tip: explore at least one Learning Center lesson to further strengthen "
                "your learner profile."
            )
    else:
        title = FRIENDLY_BLOCKED_TITLE
        message = FRIENDLY_BLOCKED_MESSAGE

    return {
        "eligible": eligible,
        "all_phases_completed": all_phases_completed,
        "wassce_optional": True,
        "wassce_recommended_now": all_phases_completed and not wassce_on_file,
        "wassce_on_file": wassce_on_file,
        "mandatory": {
            "all_levels_in_a_phase_completed": eligible,
            "phases_completed_levels": phases_with_all_levels_done,
            "focus_phase": focus_phase,
        },
        "recommended": {
            "learning_center_lesson_completed": learning_done,
            "required": False,
            "completed_lesson_count": len(completed_lessons),
        },
        "title": title,
        "message": message,
        "short_message": FRIENDLY_BLOCKED_SHORT if not eligible else message,
        "phases": phase_summaries,
    }
