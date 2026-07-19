"""phase_level_psychometric_restructure

Revision ID: phase_level_restructure
Revises: add_starter_arena_responses
Create Date: 2026-07-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "phase_level_restructure"
down_revision: Union[str, None] = "add_starter_arena_responses"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "phases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("shs_mapping", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("number"),
    )
    op.create_table(
        "levels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("phase_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("difficulty_baseline", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["phase_id"], ["phases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phase_id", "number", name="uq_level_phase_number"),
    )
    op.create_index("ix_levels_phase_id", "levels", ["phase_id"])

    op.create_table(
        "user_phase_progress",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phase_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["phase_id"], ["phases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "phase_id", name="uq_user_phase"),
    )
    op.create_index("ix_user_phase_progress_user_id", "user_phase_progress", ["user_id"])
    op.create_index("ix_user_phase_progress_phase_id", "user_phase_progress", ["phase_id"])

    op.create_table(
        "user_level_progress",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("level_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["level_id"], ["levels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "level_id", name="uq_user_level"),
    )
    op.create_index("ix_user_level_progress_user_id", "user_level_progress", ["user_id"])
    op.create_index("ix_user_level_progress_level_id", "user_level_progress", ["level_id"])

    op.create_table(
        "user_subject_performance",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject", sa.String(length=50), nullable=False),
        sa.Column("rolling_accuracy", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("current_difficulty_adjustment", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("weak_level_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "subject", name="uq_user_subject_perf"),
    )
    op.create_index("ix_user_subject_performance_user_id", "user_subject_performance", ["user_id"])

    op.create_table(
        "psychometric_questions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("bank_id", sa.String(length=32), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bank_id"),
        sa.UniqueConstraint("number"),
    )
    op.create_index("ix_psychometric_questions_category", "psychometric_questions", ["category"])

    op.create_table(
        "psychometric_options",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=1), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("trait_tags", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("programme_affinity_tags", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["question_id"], ["psychometric_questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_id", "label", name="uq_psycho_option_question_label"),
    )
    op.create_index("ix_psychometric_options_question_id", "psychometric_options", ["question_id"])

    op.create_table(
        "user_psychometric_bank_responses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("option_id", sa.Integer(), nullable=False),
        sa.Column("phase_id", sa.Integer(), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["option_id"], ["psychometric_options.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["phase_id"], ["phases.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["question_id"], ["psychometric_questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "question_id", "phase_id", name="uq_user_psycho_bank_phase_question"
        ),
    )

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phase_id", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("programme_suggestions", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("rationale_summary", sa.Text(), nullable=False),
        sa.Column("is_final", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["phase_id"], ["phases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recommendations_user_id", "recommendations", ["user_id"])
    op.create_index("ix_recommendations_phase_id", "recommendations", ["phase_id"])

    op.add_column(
        "challenge_sessions",
        sa.Column("level_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "challenge_sessions",
        sa.Column("is_replay", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.create_foreign_key(
        "fk_challenge_sessions_level_id",
        "challenge_sessions",
        "levels",
        ["level_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_challenge_sessions_level_id", "challenge_sessions", ["level_id"])

    op.add_column("challenge_responses", sa.Column("difficulty", sa.Integer(), nullable=True))
    op.add_column(
        "challenge_responses",
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("challenge_responses", "answered_at")
    op.drop_column("challenge_responses", "difficulty")
    op.drop_index("ix_challenge_sessions_level_id", table_name="challenge_sessions")
    op.drop_constraint("fk_challenge_sessions_level_id", "challenge_sessions", type_="foreignkey")
    op.drop_column("challenge_sessions", "is_replay")
    op.drop_column("challenge_sessions", "level_id")
    op.drop_table("recommendations")
    op.drop_table("user_psychometric_bank_responses")
    op.drop_table("psychometric_options")
    op.drop_table("psychometric_questions")
    op.drop_table("user_subject_performance")
    op.drop_table("user_level_progress")
    op.drop_table("user_phase_progress")
    op.drop_table("levels")
    op.drop_table("phases")
