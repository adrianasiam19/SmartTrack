"""Learner activity snapshot — signals the Notification Engine monitors (Stage 6)."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assessment.models import CurriculumLesson
from app.notifications.types import MONITORED_SIGNALS
from app.phases.models import Level, Phase, UserLevelProgress, UserPhaseProgress
from app.users.models import User
from app.users.gamification import STREAK_LAST_DATE_KEY

logger = logging.getLogger(__name__)


async def get_learner_activity_snapshot(
    db: AsyncSession,
    user: User,
) -> dict[str, Any]:
    """
    Collect the learner signals Stage 6 is responsible for monitoring.

    Stage 7 turns these into intelligent notifications.
    """
    user_id = user.id
    profile = user.learner_profile if isinstance(user.learner_profile, dict) else {}

    phase_rows = (
        await db.execute(
            select(UserPhaseProgress).where(UserPhaseProgress.user_id == user_id)
        )
    ).scalars().all()
    level_rows = (
        await db.execute(
            select(UserLevelProgress).where(UserLevelProgress.user_id == user_id)
        )
    ).scalars().all()

    completed_phases = sorted(
        [p.phase_id for p in phase_rows if (p.status or "") == "completed"]
    )
    completed_levels = [lp for lp in level_rows if (lp.status or "") == "completed"]
    in_progress_levels = [lp for lp in level_rows if (lp.status or "") == "in_progress"]

    last_completed_level: dict[str, Any] | None = None
    if completed_levels:
        dated = [lp for lp in completed_levels if getattr(lp, "completed_at", None)]
        pick = max(dated, key=lambda x: x.completed_at) if dated else completed_levels[-1]
        level = (
            await db.execute(select(Level).where(Level.id == pick.level_id))
        ).scalar_one_or_none()
        if level:
            phase = (
                await db.execute(select(Phase).where(Phase.id == level.phase_id))
            ).scalar_one_or_none()
            last_completed_level = {
                "level_id": level.id,
                "level_number": level.number,
                "phase_id": level.phase_id,
                "phase_number": phase.number if phase else None,
                "completed_at": getattr(pick, "completed_at", None),
            }

    last_completed_phase: dict[str, Any] | None = None
    completed_phase_progress = [p for p in phase_rows if (p.status or "") == "completed"]
    if completed_phase_progress:
        dated = [p for p in completed_phase_progress if getattr(p, "completed_at", None)]
        pick = max(dated, key=lambda x: x.completed_at) if dated else completed_phase_progress[-1]
        phase = (
            await db.execute(select(Phase).where(Phase.id == pick.phase_id))
        ).scalar_one_or_none()
        last_completed_phase = {
            "phase_id": pick.phase_id,
            "phase_number": phase.number if phase else None,
            "phase_name": phase.name if phase else None,
            "completed_at": getattr(pick, "completed_at", None),
        }

    continue_point: dict[str, Any] | None = None
    if in_progress_levels:
        # Prefer the lowest phase/level number still in progress
        candidates: list[tuple[int, int, UserLevelProgress, Level, Phase]] = []
        for lp in in_progress_levels:
            level = (
                await db.execute(select(Level).where(Level.id == lp.level_id))
            ).scalar_one_or_none()
            if not level:
                continue
            phase = (
                await db.execute(select(Phase).where(Phase.id == level.phase_id))
            ).scalar_one_or_none()
            if not phase:
                continue
            candidates.append((phase.number, level.number, lp, level, phase))
        if candidates:
            candidates.sort(key=lambda t: (t[0], t[1]))
            phase_n, level_n, _lp, level, phase = candidates[0]
            continue_point = {
                "phase_id": phase.id,
                "phase_number": phase_n,
                "phase_name": phase.name,
                "level_id": level.id,
                "level_number": level_n,
                "label": f"Continue from Phase {phase_n} • Level {level_n}.",
            }

    recent = profile.get("learning_recent") or profile.get("recent") or []
    if not isinstance(recent, list):
        recent = []
    bookmarks = profile.get("learning_bookmarks") or profile.get("bookmarks") or []
    if not isinstance(bookmarks, list):
        bookmarks = []
    completed_lessons = profile.get("completed_lessons") or []
    if not isinstance(completed_lessons, list):
        completed_lessons = []

    last_recent = recent[0] if recent else None
    last_visited_at = None
    if isinstance(last_recent, dict):
        last_visited_at = last_recent.get("visited_at")

    lesson_count = (
        await db.execute(select(func.count()).select_from(CurriculumLesson))
    ).scalar_one()

    wassce = profile.get("wassce") or profile.get("wassce_results") or {}
    wassce_uploaded = bool(
        wassce
        or getattr(user, "wassce_uploaded", False)
        or profile.get("wassce_uploaded")
        or profile.get("academic_results_uploaded")
    )

    # Recommendation eligibility (real gate used by Stage 7)
    rec_eligible = False
    rec_payload: dict[str, Any] = {}
    try:
        from app.recommendations.eligibility import evaluate_recommendation_eligibility

        rec_payload = await evaluate_recommendation_eligibility(db, user)
        rec_eligible = bool(rec_payload.get("eligible"))
    except Exception:
        logger.exception("Failed to evaluate recommendation eligibility for snapshot")
        rec_eligible = len(completed_phases) >= 1
        rec_payload = {
            "eligible": rec_eligible,
            "phases_completed": len(completed_phases),
        }

    snapshot = {
        "user_id": str(user_id),
        "monitored_signals": list(MONITORED_SIGNALS),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "last_completed_phase": last_completed_phase,
        "last_completed_level": last_completed_level,
        "current_learning_streak": int(getattr(user, "streak", 0) or 0),
        "streak_last_date": profile.get(STREAK_LAST_DATE_KEY),
        "challenge_progress": {
            "phases_completed": len(completed_phases),
            "levels_completed": len(completed_levels),
            "levels_in_progress": len(in_progress_levels),
            "continue_point": continue_point,
        },
        "learning_center_activity": {
            "recent_count": len(recent),
            "bookmark_count": len(bookmarks),
            "completed_lesson_count": len(completed_lessons),
            "catalogue_lessons": int(lesson_count or 0),
            "last_recent": last_recent,
            "last_visited_at": last_visited_at,
        },
        "wassce_upload_status": {
            "uploaded": wassce_uploaded,
            "details": wassce if isinstance(wassce, dict) else {},
        },
        "recommendation_eligibility": {
            "eligible": rec_eligible,
            "phases_completed": len(completed_phases),
            "likely_eligible": rec_eligible,
            "details": {
                "title": rec_payload.get("title"),
                "phases_completed_levels": (rec_payload.get("mandatory") or {}).get(
                    "phases_completed_levels"
                ),
            },
        },
        "achievement_milestones": {
            "xp": int(getattr(user, "xp", 0) or 0),
            "rank": getattr(user, "rank", None),
            "starter_arena_completed": bool(
                getattr(user, "starter_arena_completed", False)
                or profile.get("starter_arena_completed")
            ),
        },
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    return snapshot
