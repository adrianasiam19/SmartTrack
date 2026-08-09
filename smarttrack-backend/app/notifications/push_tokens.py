"""Push device / subscription tokens — Stage 9 architecture for future FCM / Web Push."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NotificationPushToken(Base):
    """
    Stores client push endpoints without sending anything yet.

    provider:
      • fcm      — Firebase Cloud Messaging device token
      • web_push — Browser PushSubscription endpoint (+ keys in endpoint_meta JSON text)
    """

    __tablename__ = "notification_push_tokens"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "provider",
            "token",
            name="uq_notification_push_token_user_provider_token",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Optional JSON string for Web Push keys (p256dh, auth) etc.
    endpoint_meta: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<NotificationPushToken id={self.id} provider={self.provider} "
            f"user_id={self.user_id} active={self.is_active}>"
        )
