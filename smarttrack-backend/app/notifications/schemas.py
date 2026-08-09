"""Pydantic schemas for the notifications API (Stage 6)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.notifications.types import priority_label


class NotificationPublic(BaseModel):
    """
    Public notification shape.

    Includes Stage 6 names (category, read_status, action_link, priority)
    plus compatibility aliases (type, is_read).
    """

    id: uuid.UUID
    user_id: uuid.UUID | None = None
    title: str
    message: str
    category: str
    type: str
    created_at: datetime
    read_status: bool
    is_read: bool
    action_link: str | None = None
    priority: str = "normal"
    priority_value: int = 1
    data: dict[str, Any] | None = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _from_orm_row(cls, value: Any) -> Any:
        if not hasattr(value, "id"):
            return value
        data = getattr(value, "data", None)
        action = getattr(value, "action_link", None)
        if not action and isinstance(data, dict):
            action = data.get("href") or data.get("action_link")
        category = getattr(value, "category", None) or getattr(value, "type", "system")
        ntype = getattr(value, "type", None) or category
        is_read = bool(getattr(value, "is_read", False))
        pval = int(getattr(value, "priority", 1) or 1)
        return {
            "id": value.id,
            "user_id": getattr(value, "user_id", None),
            "title": value.title,
            "message": value.message,
            "category": category,
            "type": ntype,
            "created_at": value.created_at,
            "read_status": is_read,
            "is_read": is_read,
            "action_link": action,
            "priority": priority_label(pval),
            "priority_value": pval,
            "data": data,
        }


class NotificationListResponse(BaseModel):
    notifications: list[NotificationPublic]
    unread_count: int


class UnreadCountResponse(BaseModel):
    unread_count: int = Field(ge=0)


class MarkReadResponse(BaseModel):
    id: uuid.UUID
    is_read: bool
    read_status: bool | None = None

    @model_validator(mode="after")
    def _sync_read(self) -> MarkReadResponse:
        if self.read_status is None:
            self.read_status = self.is_read
        return self


class MarkAllReadResponse(BaseModel):
    updated: int


class LearnerActivitySnapshotResponse(BaseModel):
    """Stage 6 monitor output — used by Stage 7 intelligent rules."""

    snapshot: dict[str, Any]


class NotificationEngineRunResponse(BaseModel):
    """Stage 7 engine run result."""

    ran: bool
    created: int
    rules_fired: list[str] = Field(default_factory=list)


class PushTokenRegisterRequest(BaseModel):
    """Stage 9 — store a client push endpoint (no send yet)."""

    provider: str = Field(description="fcm | web_push")
    token: str = Field(min_length=8, max_length=4096)
    platform: str | None = Field(default="unknown", max_length=20)
    endpoint_meta: dict[str, Any] | None = None


class PushTokenPublic(BaseModel):
    id: uuid.UUID
    provider: str
    platform: str | None = None
    is_active: bool
    created_at: datetime
    last_seen_at: datetime

    model_config = {"from_attributes": True}


class PushTokenRegisterResponse(BaseModel):
    token: PushTokenPublic
    push_enabled: bool = False
    note: str = (
        "Token stored. Push delivery is not active yet — "
        "enable PUSH_NOTIFICATIONS_ENABLED and credentials when ready."
    )


class PushTokenDeleteRequest(BaseModel):
    token: str = Field(min_length=8, max_length=4096)
    provider: str | None = None


class PushTokenDeleteResponse(BaseModel):
    deactivated: int


class DeliveryArchitectureResponse(BaseModel):
    """Describes the Stage 9 generation / delivery split for operators."""

    generation: str
    delivery: str
    active_channels: list[str]
    push_notifications_enabled: bool
    fcm_credentials_configured: bool
    web_push_vapid_configured: bool
