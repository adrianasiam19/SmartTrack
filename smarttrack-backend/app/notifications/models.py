"""ORM model for persisted in-app notifications (Stage 6)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Notification(Base):
    """
    Atlas Notification model.

    Spec fields:
      id, userId, title, message, category, createdAt,
      readStatus, actionLink, priority
    """

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    # category is the Stage-6 name; `type` kept for backward-compatible clients
    category: Mapped[str] = mapped_column(String(40), nullable=False, default="system", index=True)
    type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    action_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # 0=low, 1=normal, 2=high, 3=urgent
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1, index=True)
    # Optional deep-link / metadata for clients and future push payloads
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<Notification id={self.id} category={self.category} "
            f"user_id={self.user_id} read={self.is_read}>"
        )
