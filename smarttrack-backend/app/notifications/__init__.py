"""In-app notifications — generation, storage, and delivery channels.

Stage 9 architecture
────────────────────
Generation : service.create_notification, engine, events
Delivery   : delivery.dispatch_notification → InApp / FCM stub / Web Push stub
"""
from __future__ import annotations

from .activity import get_learner_activity_snapshot
from .delivery import (
    DeliveryPayload,
    InAppDelivery,
    PushDelivery,
    WebPushDelivery,
    dispatch_notification,
    get_delivery_channels,
)
from .engine import run_notification_engine
from .models import Notification
from .push_tokens import NotificationPushToken
from .service import (
    create_notification,
    list_notifications,
    mark_all_read,
    mark_read,
    unread_count,
)
from .types import (
    MONITORED_SIGNALS,
    NotificationCategory,
    NotificationPriority,
    NotificationType,
)

__all__ = [
    "DeliveryPayload",
    "InAppDelivery",
    "MONITORED_SIGNALS",
    "Notification",
    "NotificationCategory",
    "NotificationPriority",
    "NotificationPushToken",
    "NotificationType",
    "PushDelivery",
    "WebPushDelivery",
    "create_notification",
    "dispatch_notification",
    "get_delivery_channels",
    "get_learner_activity_snapshot",
    "list_notifications",
    "mark_all_read",
    "mark_read",
    "run_notification_engine",
    "unread_count",
]
