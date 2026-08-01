"""Authenticated in-app notifications API."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.notifications.schemas import (
    MarkAllReadResponse,
    MarkReadResponse,
    NotificationListResponse,
    NotificationPublic,
    UnreadCountResponse,
)
from app.notifications.service import (
    list_notifications,
    mark_all_read,
    mark_read,
    unread_count,
)
from app.notifications.backfill import ensure_progress_backfill
from app.users.models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = Query(default=40, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ensure_progress_backfill(db, current_user)
    await db.refresh(current_user)
    rows = await list_notifications(
        db,
        current_user.id,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )
    count = await unread_count(db, current_user.id)
    return NotificationListResponse(
        notifications=[NotificationPublic.model_validate(r) for r in rows],
        unread_count=count,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ensure_progress_backfill(db, current_user)
    count = await unread_count(db, current_user.id)
    return UnreadCountResponse(unread_count=count)


@router.post("/{notification_id}/read", response_model=MarkReadResponse)
async def read_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await mark_read(db, current_user.id, notification_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found.")
    return MarkReadResponse(id=row.id, is_read=row.is_read)


@router.post("/read-all", response_model=MarkAllReadResponse)
async def read_all_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated = await mark_all_read(db, current_user.id)
    return MarkAllReadResponse(updated=updated)
