"""Stage 9 — register / deactivate push tokens (no Firebase send yet)."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.push_tokens import NotificationPushToken

logger = logging.getLogger(__name__)

PushProvider = Literal["fcm", "web_push"]
PushPlatform = Literal["web", "android", "ios", "unknown"]


async def upsert_push_token(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    provider: PushProvider | str,
    token: str,
    platform: PushPlatform | str | None = None,
    endpoint_meta: dict[str, Any] | None = None,
) -> NotificationPushToken:
    """Create or refresh a push token for later FCM / Web Push delivery."""
    provider_key = str(provider or "").strip().lower()
    if provider_key not in {"fcm", "web_push"}:
        raise ValueError("provider must be 'fcm' or 'web_push'")
    token_value = (token or "").strip()
    if not token_value:
        raise ValueError("token is required")

    meta_raw = None
    if endpoint_meta is not None:
        meta_raw = json.dumps(endpoint_meta)

    result = await db.execute(
        select(NotificationPushToken).where(
            NotificationPushToken.user_id == user_id,
            NotificationPushToken.provider == provider_key,
            NotificationPushToken.token == token_value,
        )
    )
    row = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if row:
        row.is_active = True
        row.last_seen_at = now
        row.platform = (str(platform).strip() if platform else row.platform) or "unknown"
        if meta_raw is not None:
            row.endpoint_meta = meta_raw
        await db.flush()
        return row

    row = NotificationPushToken(
        user_id=user_id,
        provider=provider_key,
        token=token_value,
        platform=(str(platform).strip() if platform else None) or "unknown",
        endpoint_meta=meta_raw,
        is_active=True,
        created_at=now,
        last_seen_at=now,
    )
    db.add(row)
    await db.flush()
    return row


async def deactivate_push_token(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    token: str,
    provider: PushProvider | str | None = None,
) -> int:
    """Mark matching tokens inactive (logout / permission revoked)."""
    token_value = (token or "").strip()
    if not token_value:
        return 0
    stmt = select(NotificationPushToken).where(
        NotificationPushToken.user_id == user_id,
        NotificationPushToken.token == token_value,
        NotificationPushToken.is_active.is_(True),
    )
    if provider:
        stmt = stmt.where(NotificationPushToken.provider == str(provider).strip().lower())
    rows = (await db.execute(stmt)).scalars().all()
    for row in rows:
        row.is_active = False
        row.last_seen_at = datetime.now(timezone.utc)
    await db.flush()
    return len(rows)


async def list_active_push_tokens(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    provider: PushProvider | str | None = None,
) -> list[NotificationPushToken]:
    """Used by future PushDelivery / WebPushDelivery implementations."""
    stmt = select(NotificationPushToken).where(
        NotificationPushToken.user_id == user_id,
        NotificationPushToken.is_active.is_(True),
    )
    if provider:
        stmt = stmt.where(
            NotificationPushToken.provider == str(provider).strip().lower()
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())
