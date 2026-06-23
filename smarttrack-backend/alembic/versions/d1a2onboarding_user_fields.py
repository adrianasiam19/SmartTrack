"""add SHS onboarding + gamification fields to users

Revision ID: d1a2onboarding
Revises: c05ffeb6107b
Create Date: 2026-05-19 18:00:00.000000

Adds:
  • programme               (SHS programme: General Science / General Arts)
  • shs_level               (SHS 1, SHS 2, SHS 3, Completed SHS)
  • onboarding_completed    (bool flag)
  • xp                      (gamification XP, default 0)
  • rank                    (rank label, default "Beginner")
  • streak                  (daily streak counter, default 0)
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "d1a2onboarding"
down_revision: Union[str, None] = "c05ffeb6107b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SHS onboarding fields
    op.add_column(
        "users",
        sa.Column("programme", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("shs_level", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "onboarding_completed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # Gamification fields
    op.add_column(
        "users",
        sa.Column(
            "xp",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "rank",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'Beginner'"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "streak",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "streak")
    op.drop_column("users", "rank")
    op.drop_column("users", "xp")
    op.drop_column("users", "onboarding_completed")
    op.drop_column("users", "shs_level")
    op.drop_column("users", "programme")
