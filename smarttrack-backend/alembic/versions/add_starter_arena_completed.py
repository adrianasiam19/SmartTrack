"""add starter_arena_completed flag for one-time onboarding

Revision ID: add_starter_arena_completed
Revises: ai_curriculum_tutor
Create Date: 2026-07-17

Adds:
  • starter_arena_completed — true after the one-time Starter Arena finishes

Backfills existing users who already completed onboarding so they are not
forced through Starter Arena again.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_starter_arena_completed"
down_revision: Union[str, None] = "ai_curriculum_tutor"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "starter_arena_completed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    # Existing users who already finished onboarding should skip Starter Arena.
    op.execute(
        """
        UPDATE users
        SET starter_arena_completed = true
        WHERE onboarding_completed = true
        """
    )


def downgrade() -> None:
    op.drop_column("users", "starter_arena_completed")
