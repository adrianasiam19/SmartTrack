"""Notification service — create + query. Separated from delivery transport."""
from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.delivery import get_delivery_channels
from app.notifications.models import Notification
from app.notifications.types import NotificationType

logger = logging.getLogger(__name__)


async def create_notification(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    title: str,
    message: str,
    notification_type: NotificationType | str,
    data: dict[str, Any] | None = None,
    commit: bool = False,
) -> Notification:
    """
    Persist a notification for a user, then run delivery channels.

    Set commit=False when the caller already manages the transaction
    (preferred so notifications land with the triggering event).
    """
    ntype = (
        notification_type.value
        if isinstance(notification_type, NotificationType)
        else str(notification_type)
    )
    row = Notification(
        user_id=user_id,
        title=title[:200],
        message=message.strip(),
        type=ntype[:40],
        is_read=False,
        data=data,
    )
    db.add(row)
    await db.flush()

    for channel in get_delivery_channels():
        try:
            await channel.deliver(row)
        except Exception:
            logger.exception("Notification delivery failed for %s", row.id)

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
    result = await db.execute(stmt)
    return list(result.scalars().all())


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
