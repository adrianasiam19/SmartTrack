"""Notification generation service — create & store only (Stage 6 + Stage 9).

Generation vs delivery (Stage 9)
────────────────────────────────
• This module GENERATES notifications (validate → persist).
• Transport lives in app.notifications.delivery.dispatch_notification.
• The intelligent engine / events never talk to FCM or Web Push directly.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.delivery import dispatch_notification
from app.notifications.models import Notification
from app.notifications.types import (
    NotificationCategory,
    NotificationPriority,
    NotificationType,
    priority_from_label,
)

logger = logging.getLogger(__name__)


async def create_notification(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    title: str,
    message: str,
    notification_type: NotificationType | NotificationCategory | str | None = None,
    category: NotificationCategory | str | None = None,
    data: dict[str, Any] | None = None,
    action_link: str | None = None,
    priority: NotificationPriority | str | int = NotificationPriority.NORMAL,
    commit: bool = False,
    deliver: bool = True,
) -> Notification:
    """
    Generate + persist a notification, then hand off to the delivery pipeline.

    `deliver=False` is for tests / backfill that should skip channel fan-out.
    """
    cat = category or notification_type or NotificationCategory.SYSTEM
    ntype = cat.value if isinstance(cat, NotificationCategory) else str(cat)

    href = action_link
    if not href and isinstance(data, dict):
        href = data.get("href") or data.get("action_link")
    if isinstance(href, str):
        href = href.strip()[:500] or None
    else:
        href = None

    payload = dict(data) if isinstance(data, dict) else {}
    if href and "href" not in payload:
        payload["href"] = href

    row = Notification(
        user_id=user_id,
        title=title[:200],
        message=message.strip(),
        category=ntype[:40],
        type=ntype[:40],
        is_read=False,
        action_link=href,
        priority=priority_from_label(priority),
        data=payload or None,
    )
    db.add(row)
    await db.flush()

    if deliver:
        await dispatch_notification(row)

    if commit:
        await db.commit()
        await db.refresh(row)
    return row


async def list_notifications(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    category: str | None = None,
) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .offset(max(0, offset))
        .limit(min(max(1, limit), 100))
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    if category:
        stmt = stmt.where(
            (Notification.category == category) | (Notification.type == category)
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_notification(
    db: AsyncSession,
    user_id: uuid.UUID,
    notification_id: uuid.UUID,
) -> Notification | None:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def unread_count(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
    )
    return int(result.scalar_one() or 0)


async def mark_read(
    db: AsyncSession, user_id: uuid.UUID, notification_id: uuid.UUID
) -> Notification | None:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        return None
    if not row.is_read:
        row.is_read = True
        await db.commit()
        await db.refresh(row)
    return row


async def mark_all_read(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    await db.commit()
    return int(result.rowcount or 0)
