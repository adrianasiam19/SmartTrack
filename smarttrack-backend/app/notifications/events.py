"""Typed helpers that turn Atlas learner events into notifications."""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.service import create_notification
from app.notifications.types import NotificationType


async def notify_level_completed(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    phase_number: int,
    level_number: int,
    xp_earned: int = 0,
    score: float | None = None,
) -> None:
    xp_bit = f" You earned +{xp_earned} XP." if xp_earned > 0 else ""
    score_bit = f" Score: {int(round(score))}%." if score is not None else ""
    await create_notification(
        db,
        user_id=user_id,
        title="Level completed",
        message=f"You completed Phase {phase_number}, Level {level_number}.{score_bit}{xp_bit}",
        notification_type=NotificationType.PROGRESS,
        data={
            "event": "level_completed",
            "phase_number": phase_number,
            "level_number": level_number,
            "xp_earned": xp_earned,
            "href": "/challenges",
        },
    )


async def notify_phase_completed(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    phase_number: int,
    phase_name: str | None = None,
) -> None:
    label = phase_name or f"Phase {phase_number}"
    await create_notification(
        db,
        user_id=user_id,
        title="Phase completed",
        message=f"Congratulations! You completed {label}.",
        notification_type=NotificationType.ACHIEVEMENT,
        data={
            "event": "phase_completed",
            "phase_number": phase_number,
            "href": "/challenges",
        },
    )


async def notify_recommendation_ready(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    phase_number: int,
    is_final: bool = False,
) -> None:
    if is_final:
        title = "Final recommendations ready"
        message = (
            "Your final programme recommendations are ready. "
            "Open Recommendations to review them."
        )
    else:
        title = "Recommendations ready"
        message = (
            f"Your Phase {phase_number} programme recommendations are now available."
        )
    await create_notification(
        db,
        user_id=user_id,
        title=title,
        message=message,
        notification_type=NotificationType.RECOMMENDATION,
        data={
            "event": "recommendation_generated",
            "phase_number": phase_number,
            "is_final": is_final,
            "href": "/recommendations",
        },
    )


async def notify_recommendations_unlocked(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> None:
    await create_notification(
        db,
        user_id=user_id,
        title="Recommendations unlocked",
        message="Your programme recommendations are now available.",
        notification_type=NotificationType.RECOMMENDATION,
        data={"event": "recommendations_unlocked", "href": "/recommendations"},
    )


async def notify_psychometric_completed(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    phase_number: int,
) -> None:
    await create_notification(
        db,
        user_id=user_id,
        title="Checkpoint complete",
        message=(
            f"You finished the Phase {phase_number} psychometric checkpoint. "
            "Recommendations are being prepared."
        ),
        notification_type=NotificationType.PROGRESS,
        data={
            "event": "psychometric_completed",
            "phase_number": phase_number,
            "href": "/recommendations",
        },
    )


async def notify_starter_arena_completed(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> None:
    await create_notification(
        db,
        user_id=user_id,
        title="Starter Arena complete",
        message="You completed the Starter Arena. Your learner profile is ready.",
        notification_type=NotificationType.ACHIEVEMENT,
        data={"event": "starter_arena_completed", "href": "/dashboard"},
    )


async def notify_lesson_completed(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    title: str,
    subject: str,
    xp_earned: int,
) -> None:
    xp_bit = f" You earned +{xp_earned} XP." if xp_earned > 0 else ""
    await create_notification(
        db,
        user_id=user_id,
        title="Lesson completed",
        message=f'You finished "{title}" in {subject}.{xp_bit}',
        notification_type=NotificationType.LEARNING,
        data={
            "event": "lesson_completed",
            "subject": subject,
            "xp_earned": xp_earned,
            "href": "/learning",
        },
    )


async def notify_xp_earned(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    amount: int,
    context: str | None = None,
) -> None:
    if amount <= 0:
        return
    suffix = f" {context}" if context else ""
    await create_notification(
        db,
        user_id=user_id,
        title="XP earned",
        message=f"You earned +{amount} XP.{suffix}",
        notification_type=NotificationType.XP,
        data={"event": "xp_earned", "xp_earned": amount},
    )


async def notify_system(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    title: str,
    message: str,
    data: dict[str, Any] | None = None,
) -> None:
    await create_notification(
        db,
        user_id=user_id,
        title=title,
        message=message,
        notification_type=NotificationType.SYSTEM,
        data=data,
    )
