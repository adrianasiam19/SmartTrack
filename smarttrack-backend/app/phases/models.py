"""Phase / Level progression models."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Phase(Base):
    __tablename__ = "phases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)  # 1–3
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Internal curriculum mapping — never expose in public API schemas
    shs_mapping: Mapped[str] = mapped_column(String(20), nullable=False)

    levels: Mapped[list["Level"]] = relationship(
        "Level", back_populates="phase", order_by="Level.number"
    )


class Level(Base):
    __tablename__ = "levels"
    __table_args__ = (
        UniqueConstraint("phase_id", "number", name="uq_level_phase_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phase_id: Mapped[int] = mapped_column(
        ForeignKey("phases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1–10
    difficulty_baseline: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    phase: Mapped["Phase"] = relationship("Phase", back_populates="levels")


class UserPhaseProgress(Base):
    __tablename__ = "user_phase_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "phase_id", name="uq_user_phase"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    phase_id: Mapped[int] = mapped_column(
        ForeignKey("phases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="locked")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UserLevelProgress(Base):
    __tablename__ = "user_level_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "level_id", name="uq_user_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    level_id: Mapped[int] = mapped_column(
        ForeignKey("levels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="locked")
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UserSubjectPerformance(Base):
    __tablename__ = "user_subject_performance"
    __table_args__ = (
        UniqueConstraint("user_id", "subject", name="uq_user_subject_perf"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject: Mapped[str] = mapped_column(String(50), nullable=False)
    rolling_accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    current_difficulty_adjustment: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    weak_level_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
