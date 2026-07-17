"""add grounded AI curriculum lessons

Revision ID: ai_curriculum_tutor
Revises: add_challenge_hub_tables, add_daily_streak_progress_table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "ai_curriculum_tutor"
down_revision: Union[str, Sequence[str], None] = (
    "add_challenge_hub_tables",
    "add_daily_streak_progress_table",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "curriculum_lessons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("curriculum_id", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("subject", sa.String(length=100), nullable=False),
        sa.Column("programme", sa.String(length=20), nullable=False),
        sa.Column("shs_levels", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("unit_id", sa.String(length=100), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("xp_reward", sa.Integer(), nullable=False),
        sa.Column("source_content", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("search_text", sa.Text(), nullable=False),
        sa.Column(
            "ai_content_by_level",
            postgresql.JSON(astext_type=sa.Text()),
            server_default=sa.text("'{}'::json"),
            nullable=False,
        ),
        sa.Column(
            "ai_content_version",
            sa.String(length=30),
            server_default="v1",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("curriculum_id"),
    )
    op.create_index(
        op.f("ix_curriculum_lessons_id"), "curriculum_lessons", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_curriculum_lessons_curriculum_id"),
        "curriculum_lessons",
        ["curriculum_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_curriculum_lessons_title"),
        "curriculum_lessons",
        ["title"],
        unique=False,
    )
    op.create_index(
        op.f("ix_curriculum_lessons_subject"),
        "curriculum_lessons",
        ["subject"],
        unique=False,
    )
    op.create_index(
        op.f("ix_curriculum_lessons_programme"),
        "curriculum_lessons",
        ["programme"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_curriculum_lessons_programme"), table_name="curriculum_lessons"
    )
    op.drop_index(
        op.f("ix_curriculum_lessons_subject"), table_name="curriculum_lessons"
    )
    op.drop_index(op.f("ix_curriculum_lessons_title"), table_name="curriculum_lessons")
    op.drop_index(
        op.f("ix_curriculum_lessons_curriculum_id"),
        table_name="curriculum_lessons",
    )
    op.drop_index(op.f("ix_curriculum_lessons_id"), table_name="curriculum_lessons")
    op.drop_table("curriculum_lessons")
