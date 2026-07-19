"""Psychometric question bank models (Atlas Get-to-Know-You)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PsychometricQuestion(Base):
    __tablename__ = "psychometric_questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bank_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    options: Mapped[list["PsychometricOption"]] = relationship(
        "PsychometricOption",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="PsychometricOption.label",
    )


class PsychometricOption(Base):
    __tablename__ = "psychometric_options"
    __table_args__ = (
        UniqueConstraint("question_id", "label", name="uq_psycho_option_question_label"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("psychometric_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(1), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    trait_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)
    programme_affinity_tags: Mapped[list | None] = mapped_column(JSON, nullable=True)

    question: Mapped["PsychometricQuestion"] = relationship(
        "PsychometricQuestion", back_populates="options"
    )


class UserPsychometricBankResponse(Base):
    """Checkpoint answers against the Get-to-Know-You bank."""

    __tablename__ = "user_psychometric_bank_responses"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "question_id",
            "phase_id",
            name="uq_user_psycho_bank_phase_question",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("psychometric_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    option_id: Mapped[int] = mapped_column(
        ForeignKey("psychometric_options.id", ondelete="CASCADE"),
        nullable=False,
    )
    phase_id: Mapped[int | None] = mapped_column(
        ForeignKey("phases.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
