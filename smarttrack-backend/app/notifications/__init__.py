"""In-app notifications — storage, creation, and delivery channels."""
from __future__ import annotations

from .delivery import InAppDelivery, get_delivery_channels
from .models import Notification
from .service import (
    create_notification,
    list_notifications,
    mark_all_read,
    mark_read,
    unread_count,
)
from .types import NotificationType

__all__ = [
    "InAppDelivery",
    "Notification",
    "NotificationType",
    "create_notification",
    "get_delivery_channels",
    "list_notifications",
    "mark_all_read",
    "mark_read",
    "unread_count",
]
