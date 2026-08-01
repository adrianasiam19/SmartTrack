"""Delivery channels — in-app now; push (FCM) can plug in later without redesign."""
from __future__ import annotations

import logging
from typing import Protocol

from app.notifications.models import Notification

logger = logging.getLogger(__name__)


class DeliveryChannel(Protocol):
    async def deliver(self, notification: Notification) -> None:
        """Send or surface a notification through this channel."""


class InAppDelivery:
    """
    Persistence is the delivery for in-app notifications.
    This channel exists so create_notification always goes through a delivery
    pipeline that can later include Firebase Cloud Messaging, email, etc.
    """

    async def deliver(self, notification: Notification) -> None:
        logger.debug(
            "In-app notification ready user=%s type=%s id=%s",
            notification.user_id,
            notification.type,
            notification.id,
        )


def get_delivery_channels() -> list[DeliveryChannel]:
    """Active channels. Add PushDelivery here when FCM is enabled."""
    return [InAppDelivery()]
