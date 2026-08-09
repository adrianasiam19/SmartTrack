"""Merge password_resets branch with phase_level_restructure."""

from __future__ import annotations

revision = "merge_password_resets_phases"
down_revision = ("password_resets_table", "phase_level_restructure")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
