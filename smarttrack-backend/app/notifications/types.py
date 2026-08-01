"""Notification type catalogue — keep delivery-agnostic."""
from __future__ import annotations

from enum import StrEnum


class NotificationType(StrEnum):
    ACHIEVEMENT = "achievement"
    XP = "xp"
    LEARNING = "learning"
    RECOMMENDATION = "recommendation"
    PROGRESS = "progress"
    SYSTEM = "system"
