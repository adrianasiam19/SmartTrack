"""Notification categories, priorities, and monitored learner signals (Stage 6)."""
from __future__ import annotations

from enum import IntEnum, StrEnum


class NotificationCategory(StrEnum):
    """High-level notification categories (Stage 6 `category` field)."""

    ACHIEVEMENT = "achievement"
    XP = "xp"
    LEARNING = "learning"
    RECOMMENDATION = "recommendation"
    PROGRESS = "progress"
    SYSTEM = "system"
    STREAK = "streak"
    REMINDER = "reminder"


# Backward-compatible alias used across the codebase
NotificationType = NotificationCategory


class NotificationPriority(IntEnum):
    """Priority levels for sorting / future push urgency."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


PRIORITY_LABELS = {
    NotificationPriority.LOW: "low",
    NotificationPriority.NORMAL: "normal",
    NotificationPriority.HIGH: "high",
    NotificationPriority.URGENT: "urgent",
}


def priority_label(value: int | NotificationPriority | None) -> str:
    try:
        return PRIORITY_LABELS[NotificationPriority(int(value if value is not None else 1))]
    except Exception:
        return "normal"


def priority_from_label(label: str | int | NotificationPriority | None) -> int:
    if isinstance(label, NotificationPriority):
        return int(label)
    if isinstance(label, int):
        return max(0, min(3, label))
    key = str(label or "normal").strip().lower()
    for p, name in PRIORITY_LABELS.items():
        if name == key:
            return int(p)
    return int(NotificationPriority.NORMAL)


# Signals the Notification Engine monitors (Stage 6 foundation; Stage 7 uses these).
MONITORED_SIGNALS = (
    "last_login",
    "last_completed_phase",
    "last_completed_level",
    "current_learning_streak",
    "challenge_progress",
    "learning_center_activity",
    "wassce_upload_status",
    "recommendation_eligibility",
    "achievement_milestones",
)
