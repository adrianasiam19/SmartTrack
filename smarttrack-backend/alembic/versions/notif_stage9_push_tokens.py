"""Stage 9 — notification_push_tokens for future FCM / Web Push."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "notif_stage9_push_tokens"
down_revision = "notif_stage6_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_push_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("token", sa.Text(), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=True),
        sa.Column("endpoint_meta", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "provider",
            "token",
            name="uq_notification_push_token_user_provider_token",
        ),
    )
    op.create_index(
        "ix_notification_push_tokens_user_id",
        "notification_push_tokens",
        ["user_id"],
    )
    op.create_index(
        "ix_notification_push_tokens_provider",
        "notification_push_tokens",
        ["provider"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_push_tokens_provider",
        table_name="notification_push_tokens",
    )
    op.drop_index(
        "ix_notification_push_tokens_user_id",
        table_name="notification_push_tokens",
    )
    op.drop_table("notification_push_tokens")
