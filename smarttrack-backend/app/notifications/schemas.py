"""Pydantic schemas for the notifications API."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class NotificationPublic(BaseModel):
    id: uuid.UUID
    title: str
    message: str
    type: str
    is_read: bool
    data: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    notifications: list[NotificationPublic]
    unread_count: int


class UnreadCountResponse(BaseModel):
    unread_count: int = Field(ge=0)


class MarkReadResponse(BaseModel):
    id: uuid.UUID
    is_read: bool


class MarkAllReadResponse(BaseModel):
    updated: int
