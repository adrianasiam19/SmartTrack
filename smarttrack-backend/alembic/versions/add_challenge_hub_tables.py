"""Add challenge_sessions and challenge_responses tables for the Adaptive Challenge Hub

Revision ID: add_challenge_hub_tables
Revises: psychometric_responses
Create Date: 2026-07-16

Adds:
  • challenge_sessions      (tracks session state, XP, subject progress)
  • challenge_responses     (individual answers with question data for adaptive learning)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "add_challenge_hub_tables"
down_revision: Union[str, None] = "psychometric_responses"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── challenge_sessions ────────────────────────────────────────────────
    op.create_table(
        "challenge_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("challenge_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="in_progress",
        ),
        sa.Column("total_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wrong_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "current_subject_index", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "started_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "completed_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Indexes for user_id are created via column index=True above.
    op.create_index(
        op.f("ix_challenge_sessions_id"),
        "challenge_sessions",
        ["id"],
        unique=False,
    )

    # ── challenge_responses ───────────────────────────────────────────────
    op.create_table(
        "challenge_responses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "session_id",
            sa.Integer(),
            sa.ForeignKey("challenge_sessions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("subject", sa.String(length=50), nullable=False),
        sa.Column("question_index", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column(
            "question_type", sa.String(length=30), nullable=False, server_default="mcq"
        ),
        sa.Column("options", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("correct_answer", sa.String(length=500), nullable=False),
        sa.Column("user_answer", sa.String(length=500), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("time_taken_seconds", sa.Float(), nullable=True),
        sa.Column("xp_earned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Indexes for session_id/user_id are created via column index=True above.
    op.create_index(
        op.f("ix_challenge_responses_id"),
        "challenge_responses",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_challenge_responses_user_id"), table_name="challenge_responses"
    )
    op.drop_index(
        op.f("ix_challenge_responses_session_id"), table_name="challenge_responses"
    )
    op.drop_index(
        op.f("ix_challenge_responses_id"), table_name="challenge_responses"
    )
    op.drop_table("challenge_responses")
    op.drop_index(
        op.f("ix_challenge_sessions_user_id"), table_name="challenge_sessions"
    )
    op.drop_index(
        op.f("ix_challenge_sessions_id"), table_name="challenge_sessions"
    )
    op.drop_table("challenge_sessions")
