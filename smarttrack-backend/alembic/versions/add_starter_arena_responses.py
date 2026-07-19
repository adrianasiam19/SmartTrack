"""persist adaptive starter arena responses and learner profile

Revision ID: add_starter_arena_responses
Revises: add_starter_arena_completed
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "add_starter_arena_responses"
down_revision: Union[str, None] = "add_starter_arena_completed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "learner_profile",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.create_table(
        "starter_arena_responses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.String(length=120), nullable=False),
        sa.Column("question_id", sa.String(length=120), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=30), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("cognitive_skill", sa.String(length=100), nullable=True),
        sa.Column("question_format", sa.String(length=40), nullable=False),
        sa.Column("options", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=True),
        sa.Column("time_taken_seconds", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "session_id",
            "question_id",
            name="uq_starter_response_user_session_question",
        ),
    )
    op.create_index(
        op.f("ix_starter_arena_responses_id"),
        "starter_arena_responses",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_starter_arena_responses_user_id"),
        "starter_arena_responses",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_starter_arena_responses_session_id"),
        "starter_arena_responses",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_starter_arena_responses_session_id"),
        table_name="starter_arena_responses",
    )
    op.drop_index(
        op.f("ix_starter_arena_responses_user_id"),
        table_name="starter_arena_responses",
    )
    op.drop_index(
        op.f("ix_starter_arena_responses_id"),
        table_name="starter_arena_responses",
    )
    op.drop_table("starter_arena_responses")
    op.drop_column("users", "learner_profile")
