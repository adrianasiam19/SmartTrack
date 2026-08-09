"""Authenticated in-app notifications API."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.notifications.schemas import (
    DeliveryArchitectureResponse,
    LearnerActivitySnapshotResponse,
    MarkAllReadResponse,
    MarkReadResponse,
    NotificationEngineRunResponse,
    NotificationListResponse,
    NotificationPublic,
    PushTokenDeleteRequest,
    PushTokenDeleteResponse,
    PushTokenPublic,
    PushTokenRegisterRequest,
    PushTokenRegisterResponse,
    UnreadCountResponse,
)
from app.notifications.service import (
    list_notifications,
    mark_all_read,
    mark_read,
    unread_count,
)
from app.notifications.activity import get_learner_activity_snapshot
from app.notifications.backfill import ensure_progress_backfill
from app.notifications.delivery import get_delivery_channels
from app.notifications.engine import run_notification_engine
from app.notifications.push_service import deactivate_push_token, upsert_push_token
from app.config import settings
from app.users.models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = Query(default=40, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False),
    category: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ensure_progress_backfill(db, current_user)
    await db.refresh(current_user)
    # Stage 7 — evaluate intelligent reminder rules (throttled)
    try:
        await run_notification_engine(db, current_user)
        await db.refresh(current_user)
    except Exception:
        import logging

        logging.getLogger(__name__).exception("Notification engine failed")
    rows = await list_notifications(
        db,
        current_user.id,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
        category=category,
    )
    count = await unread_count(db, current_user.id)
    return NotificationListResponse(
        notifications=[NotificationPublic.model_validate(r) for r in rows],
        unread_count=count,
    )


@router.get("/activity-snapshot", response_model=LearnerActivitySnapshotResponse)
async def activity_snapshot(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Stage 6 monitor endpoint — returns the learner signals the Notification
    Engine tracks. Stage 7 uses this to generate intelligent reminders.
    """
    snapshot = await get_learner_activity_snapshot(db, current_user)
    return LearnerActivitySnapshotResponse(snapshot=snapshot)


@router.post("/engine/run", response_model=NotificationEngineRunResponse)
async def run_engine(
    force: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually evaluate Stage 7 intelligent notification rules for this user."""
    result = await run_notification_engine(db, current_user, force=force)
    return NotificationEngineRunResponse(**result)


@router.get("/delivery-architecture", response_model=DeliveryArchitectureResponse)
async def delivery_architecture(
    current_user: User = Depends(get_current_user),
):
    """
    Stage 9 — inspect generation vs delivery split.
    Confirms push is prepared but inactive until credentials are set.
    """
    _ = current_user
    return DeliveryArchitectureResponse(
        generation=(
            "service.create_notification / engine / events persist Notification rows"
        ),
        delivery=(
            "delivery.dispatch_notification fans out DeliveryPayload to channels"
        ),
        active_channels=[c.name for c in get_delivery_channels()],
        push_notifications_enabled=bool(settings.PUSH_NOTIFICATIONS_ENABLED),
        fcm_credentials_configured=bool(
            settings.FCM_CREDENTIALS_JSON or settings.FCM_CREDENTIALS_PATH
        ),
        web_push_vapid_configured=bool(
            settings.WEB_PUSH_VAPID_PUBLIC_KEY and settings.WEB_PUSH_VAPID_PRIVATE_KEY
        ),
    )


@router.post("/push-tokens", response_model=PushTokenRegisterResponse)
async def register_push_token(
    body: PushTokenRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Stage 9 — register an FCM / Web Push token for this user.

    Tokens are stored only. No Firebase or Web Push send happens yet.
    """
    try:
        row = await upsert_push_token(
            db,
            user_id=current_user.id,
            provider=body.provider,
            token=body.token,
            platform=body.platform,
            endpoint_meta=body.endpoint_meta,
        )
        await db.commit()
        await db.refresh(row)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return PushTokenRegisterResponse(
        token=PushTokenPublic.model_validate(row),
        push_enabled=bool(settings.PUSH_NOTIFICATIONS_ENABLED),
    )


@router.delete("/push-tokens", response_model=PushTokenDeleteResponse)
async def delete_push_token(
    body: PushTokenDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a stored push token (e.g. on logout)."""
    count = await deactivate_push_token(
        db,
        user_id=current_user.id,
        token=body.token,
        provider=body.provider,
    )
    await db.commit()
    return PushTokenDeleteResponse(deactivated=count)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ensure_progress_backfill(db, current_user)
    try:
        await run_notification_engine(db, current_user)
    except Exception:
        import logging

        logging.getLogger(__name__).exception("Notification engine failed")
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
