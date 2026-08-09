"""Stage 6 — add category, action_link, priority to notifications."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "notif_stage6_fields"
down_revision = "add_in_app_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "notifications",
        sa.Column("category", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "notifications",
        sa.Column("action_link", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "notifications",
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
    )
    # Backfill category from legacy type column
    op.execute(
        sa.text(
            "UPDATE notifications SET category = type WHERE category IS NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE notifications SET action_link = data->>'href' "
            "WHERE action_link IS NULL AND data IS NOT NULL"
        )
    )
    op.alter_column("notifications", "category", nullable=False)
    op.create_index("ix_notifications_category", "notifications", ["category"])
    op.create_index("ix_notifications_priority", "notifications", ["priority"])


def downgrade() -> None:
    op.drop_index("ix_notifications_priority", table_name="notifications")
    op.drop_index("ix_notifications_category", table_name="notifications")
    op.drop_column("notifications", "priority")
    op.drop_column("notifications", "action_link")
    op.drop_column("notifications", "category")
