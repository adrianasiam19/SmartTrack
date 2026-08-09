"""Stage 9 — Notification delivery channels.

Architecture
────────────
Generation (service / engine / events)
    → persists a Notification row
    → calls dispatch_notification()

Delivery (this module)
    → builds a channel-agnostic DeliveryPayload
    → fans out to every active DeliveryChannel

Today: InAppDelivery only (DB row is the source of truth for the bell).

Later (no Notification Engine changes required):
    • enable PUSH_NOTIFICATIONS_ENABLED
    • register FCM / Web Push credentials in settings
    • implement send logic inside PushDelivery / WebPushDelivery
    • clients register tokens via /notifications/push-tokens
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol

from app.config import settings
from app.notifications.models import Notification
from app.notifications.types import priority_label

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeliveryPayload:
    """
    Channel-agnostic payload.

    Push providers (FCM, Web Push) should consume this DTO — never the ORM
    row or the generation rules — so the engine stays transport-agnostic.
    """

    notification_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str
    category: str
    priority: str
    priority_value: int
    action_link: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_notification(cls, row: Notification) -> DeliveryPayload:
        data = dict(row.data) if isinstance(row.data, dict) else {}
        action = row.action_link or data.get("href") or data.get("action_link")
        if isinstance(action, str):
            action = action.strip() or None
        else:
            action = None
        category = getattr(row, "category", None) or row.type or "system"
        pval = int(getattr(row, "priority", 1) or 1)
        return cls(
            notification_id=row.id,
            user_id=row.user_id,
            title=row.title,
            message=row.message,
            category=str(category),
            priority=priority_label(pval),
            priority_value=pval,
            action_link=action,
            data=data,
        )

    def as_push_data(self) -> dict[str, str]:
        """Flat string map suitable for FCM data / Web Push custom data."""
        out: dict[str, str] = {
            "notification_id": str(self.notification_id),
            "category": self.category,
            "priority": self.priority,
        }
        if self.action_link:
            out["action_link"] = self.action_link
        for key, value in self.data.items():
            if value is None:
                continue
            out[str(key)] = value if isinstance(value, str) else str(value)
        return out


class DeliveryChannel(Protocol):
    """Transport adapter. Generation never imports concrete channels."""

    name: str

    async def deliver(self, payload: DeliveryPayload) -> None:
        """Send or surface one notification through this channel."""


class InAppDelivery:
    """
    In-app channel.

    Persistence already happened in generation; this channel confirms the
    notification is available for the Dashboard bell to poll.
    """

    name = "in_app"

    async def deliver(self, payload: DeliveryPayload) -> None:
        logger.debug(
            "In-app delivery ready user=%s category=%s id=%s priority=%s",
            payload.user_id,
            payload.category,
            payload.notification_id,
            payload.priority,
        )


class PushDelivery:
    """
    Firebase Cloud Messaging stub (Stage 9 architecture only).

    Intentionally does NOT call Firebase. When enabled later:
      1. Load credentials from settings.FCM_CREDENTIALS_JSON / path
      2. Look up active tokens for payload.user_id
      3. Send notification + data via firebase_admin.messaging
    """

    name = "fcm_push"

    async def deliver(self, payload: DeliveryPayload) -> None:
        if not settings.PUSH_NOTIFICATIONS_ENABLED:
            return
        if not (settings.FCM_CREDENTIALS_JSON or settings.FCM_CREDENTIALS_PATH):
            logger.info(
                "PushDelivery skipped (no FCM credentials) notification=%s",
                payload.notification_id,
            )
            return
        # Future: import firebase_admin and send using payload.as_push_data()
        logger.info(
            "PushDelivery placeholder — FCM not implemented yet notification=%s user=%s",
            payload.notification_id,
            payload.user_id,
        )


class WebPushDelivery:
    """
    Web Push (VAPID) stub (Stage 9 architecture only).

    Intentionally does NOT send browser pushes. When enabled later:
      1. Use VAPID keys from settings
      2. Look up web push subscriptions for the user
      3. Send via pywebpush / equivalent
    """

    name = "web_push"

    async def deliver(self, payload: DeliveryPayload) -> None:
        if not settings.PUSH_NOTIFICATIONS_ENABLED:
            return
        if not (
            settings.WEB_PUSH_VAPID_PUBLIC_KEY and settings.WEB_PUSH_VAPID_PRIVATE_KEY
        ):
            logger.debug(
                "WebPushDelivery skipped (no VAPID keys) notification=%s",
                payload.notification_id,
            )
            return
        logger.info(
            "WebPushDelivery placeholder — Web Push not implemented yet notification=%s user=%s",
            payload.notification_id,
            payload.user_id,
        )


def get_delivery_channels() -> list[DeliveryChannel]:
    """
    Active delivery pipeline.

    Always includes InAppDelivery. Push stubs are registered so enabling
    PUSH_NOTIFICATIONS_ENABLED activates them without touching the engine.
    """
    channels: list[DeliveryChannel] = [InAppDelivery()]
    # Stubs stay in the pipeline; they no-op until credentials + flag are set.
    channels.append(PushDelivery())
    channels.append(WebPushDelivery())
    return channels


async def dispatch_notification(notification: Notification) -> None:
    """
    Delivery entry point — called AFTER generation persists the row.

    Failures in one channel never roll back generation and never block others.
    """
    payload = DeliveryPayload.from_notification(notification)
    for channel in get_delivery_channels():
        try:
            await channel.deliver(payload)
        except Exception:
            logger.exception(
                "Notification delivery failed channel=%s id=%s",
                getattr(channel, "name", type(channel).__name__),
                payload.notification_id,
            )
