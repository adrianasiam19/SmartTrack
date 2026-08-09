"""One-time backfill of notifications from existing learner progress."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.notifications.models import Notification
from app.notifications.types import NotificationType
from app.phases.models import Level, Phase, UserLevelProgress, UserPhaseProgress
from app.recommendations.models import Recommendation
from app.users.models import User

logger = logging.getLogger(__name__)

BACKFILL_FLAG = "notifications_backfilled"


def _as_utc(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _add_row(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    title: str,
    message: str,
    notification_type: NotificationType,
    created_at: datetime | None,
    data: dict[str, Any] | None = None,
    is_read: bool = True,
) -> Notification:
    """Historical rows default to read so the badge stays calm after backfill."""
    href = None
    if isinstance(data, dict):
        raw = data.get("href") or data.get("action_link")
        href = str(raw)[:500] if raw else None
    row = Notification(
        user_id=user_id,
        title=title[:200],
        message=message.strip(),
        category=notification_type.value,
        type=notification_type.value,
        is_read=is_read,
        action_link=href,
        priority=1,
        data=data,
        created_at=_as_utc(created_at),
    )
    db.add(row)
    return row


async def ensure_progress_backfill(db: AsyncSession, user: User) -> int:
    """
    If this learner already had progress before notifications existed,
    create a concise history once. Safe to call on every list/unread fetch.
    """
    profile: dict[str, Any] = (
        dict(user.learner_profile) if isinstance(user.learner_profile, dict) else {}
    )
    if profile.get(BACKFILL_FLAG):
        return 0

    created = 0
    user_id = user.id

    # Starter Arena
    if user.starter_arena_completed:
        _add_row(
            db,
            user_id=user_id,
            title="Starter Arena complete",
            message="You completed the Starter Arena. Your learner profile is ready.",
            notification_type=NotificationType.ACHIEVEMENT,
            created_at=user.created_at,
            data={"event": "starter_arena_completed", "href": "/dashboard", "backfill": True},
        )
        created += 1

    # Completed phases
    phase_rows = (
        await db.execute(
            select(UserPhaseProgress, Phase)
            .join(Phase, UserPhaseProgress.phase_id == Phase.id)
            .where(
                UserPhaseProgress.user_id == user_id,
                UserPhaseProgress.status == "completed",
            )
            .order_by(Phase.number.asc())
        )
    ).all()
    for upp, phase in phase_rows:
        _add_row(
            db,
            user_id=user_id,
            title="Phase completed",
            message=f"Congratulations! You completed {phase.name or f'Phase {phase.number}'}.",
            notification_type=NotificationType.ACHIEVEMENT,
            created_at=upp.completed_at or upp.started_at,
            data={
                "event": "phase_completed",
                "phase_number": phase.number,
                "href": "/challenges",
                "backfill": True,
            },
        )
        created += 1

    # Level progress summaries (per phase) — avoid 10 separate rows
    level_rows = (
        await db.execute(
            select(UserLevelProgress, Level, Phase)
            .join(Level, UserLevelProgress.level_id == Level.id)
            .join(Phase, Level.phase_id == Phase.id)
            .where(
                UserLevelProgress.user_id == user_id,
                UserLevelProgress.status == "completed",
            )
            .order_by(Phase.number.asc(), Level.number.asc())
        )
    ).all()

    by_phase: dict[int, list[tuple[UserLevelProgress, Level, Phase]]] = {}
    for ulp, level, phase in level_rows:
        by_phase.setdefault(phase.number, []).append((ulp, level, phase))

    completed_phase_numbers = {phase.number for _, phase in phase_rows}

    for phase_number, entries in by_phase.items():
        phase = entries[0][2]
        last = entries[-1]
        last_ulp, last_level, _ = last
        count = len(entries)
        # Skip verbose level summary when we already have a phase-complete notification
        if phase_number in completed_phase_numbers and count >= 10:
            continue
        score_bits = [
            float(ulp.score)
            for ulp, _, _ in entries
            if ulp.score is not None
        ]
        best = max(score_bits) if score_bits else None
        # Scores may be 0–1 or 0–100 depending on when they were stored
        if best is not None and best <= 1.0:
            best_pct = int(round(best * 100))
        elif best is not None:
            best_pct = int(round(best))
        else:
            best_pct = None
        score_msg = f" Best score: {best_pct}%." if best_pct is not None else ""
        _add_row(
            db,
            user_id=user_id,
            title=f"Phase {phase_number} progress",
            message=(
                f"You completed {count} level{'s' if count != 1 else ''} "
                f"in {phase.name or f'Phase {phase_number}'} "
                f"(up to Level {last_level.number}).{score_msg}"
            ),
            notification_type=NotificationType.PROGRESS,
            created_at=last_ulp.completed_at,
            data={
                "event": "level_progress_summary",
                "phase_number": phase_number,
                "levels_completed": count,
                "href": "/challenges",
                "backfill": True,
            },
        )
        created += 1

    # Current phase in progress (if any)
    active = (
        await db.execute(
            select(UserPhaseProgress, Phase)
            .join(Phase, UserPhaseProgress.phase_id == Phase.id)
            .where(
                UserPhaseProgress.user_id == user_id,
                UserPhaseProgress.status == "in_progress",
            )
            .order_by(Phase.number.desc())
        )
    ).first()
    if active:
        upp, phase = active
        done_in_phase = len(by_phase.get(phase.number, []))
        _add_row(
            db,
            user_id=user_id,
            title=f"Continue Phase {phase.number}",
            message=(
                f"You're on {phase.name or f'Phase {phase.number}'}"
                + (f" with {done_in_phase} level(s) done so far." if done_in_phase else ".")
                + " Keep going in Challenges."
            ),
            notification_type=NotificationType.PROGRESS,
            created_at=upp.started_at,
            data={
                "event": "phase_in_progress",
                "phase_number": phase.number,
                "href": "/challenges",
                "backfill": True,
            },
            is_read=False,  # nudge to continue
        )
        created += 1

    # Recommendations on file
    recs = (
        await db.execute(
            select(Recommendation, Phase)
            .join(Phase, Recommendation.phase_id == Phase.id)
            .where(Recommendation.user_id == user_id)
            .order_by(Recommendation.generated_at.asc())
        )
    ).all()
    seen_phases: set[int] = set()
    for rec, phase in recs:
        if phase.number in seen_phases:
            continue
        seen_phases.add(phase.number)
        title = (
            "Final recommendations ready"
            if rec.is_final
            else "Recommendations ready"
        )
        message = (
            "Your final programme recommendations are ready."
            if rec.is_final
            else f"Your Phase {phase.number} programme recommendations are available."
        )
        _add_row(
            db,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.RECOMMENDATION,
            created_at=rec.generated_at,
            data={
                "event": "recommendation_generated",
                "phase_number": phase.number,
                "href": "/recommendations",
                "backfill": True,
            },
        )
        created += 1

    # Learning Center milestones
    completed_lessons = profile.get("completed_lessons") or []
    if isinstance(completed_lessons, list) and len(completed_lessons) > 0:
        _add_row(
            db,
            user_id=user_id,
            title="Learning progress",
            message=(
                f"You've completed {len(completed_lessons)} lesson"
                f"{'s' if len(completed_lessons) != 1 else ''} in the Learning Center."
            ),
            notification_type=NotificationType.LEARNING,
            created_at=None,
            data={
                "event": "learning_milestone",
                "lessons_completed": len(completed_lessons),
                "href": "/learning",
                "backfill": True,
            },
        )
        created += 1

    # XP snapshot
    xp = int(user.xp or 0)
    if xp > 0:
        _add_row(
            db,
            user_id=user_id,
            title="XP earned",
            message=f"You have earned {xp} XP so far. Rank: {user.rank or 'Beginner'}.",
            notification_type=NotificationType.XP,
            created_at=None,
            data={"event": "xp_snapshot", "xp": xp, "backfill": True},
        )
        created += 1

    profile[BACKFILL_FLAG] = True
    profile["notifications_backfilled_at"] = datetime.now(timezone.utc).isoformat()
    user.learner_profile = profile
    flag_modified(user, "learner_profile")

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Notification backfill failed for user=%s", user_id)
        return 0

    logger.info("Backfilled %s notifications for user=%s", created, user_id)
    return created
