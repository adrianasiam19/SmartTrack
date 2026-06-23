"""add psychometric_responses table

Revision ID: psychometric_responses
Revises: 95d6d20853f2
Create Date: 2026-06-11 18:00:00.000000

Stores user answers to psychometric insight cards for recommendation engine analysis.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "psychometric_responses"
down_revision: Union[str, Sequence[str], None] = "95d6d20853f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "psychometric_responses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("card_id", sa.String(length=50), nullable=False),
        sa.Column("answer", sa.String(length=10), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_psychometric_responses_id"),
        "psychometric_responses",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_psychometric_responses_user_id"),
        "psychometric_responses",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_psychometric_responses_user_id"),
        table_name="psychometric_responses",
    )
    op.drop_index(
        op.f("ix_psychometric_responses_id"),
        table_name="psychometric_responses",
    )
    op.drop_table("psychometric_responses")
