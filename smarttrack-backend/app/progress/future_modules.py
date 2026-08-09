"""
Future Progress Dashboard modules (Stage 5).

Competitive leaderboards are deferred for MVP. This module defines a stable
extension contract so rankings can mount into the Personal Progress Dashboard
later without reshaping Stages 1–4.

To enable later:
  1. Set PROGRESS_LEADERBOARD_MODULE_ENABLED=true
  2. Implement payload builder (see build_leaderboard_module_payload)
  3. Render via ProgressExtensionSlot / LeaderboardModuleHost on the frontend
"""
from __future__ import annotations

from typing import Any

from app.config import settings
from app.progress.schemas import FutureModules, LeaderboardModuleConfig

# Planned ranking scopes — documented for future work; not active in MVP.
PLANNED_LEADERBOARD_SCOPES = (
    "global",
    "school",
    "weekly",
    "monthly",
    "friends",
)


def build_leaderboard_module_payload(_user_id: Any = None) -> dict | None:
    """
    Reserved hook for future leaderboard rows / personal rank context.

    Returns None while the module is disabled or unimplemented.
    When enabling rankings, populate a stable shape here, e.g.:
      { "scope": "weekly", "entries": [...], "viewer_rank": 12 }
    """
    if not getattr(settings, "PROGRESS_LEADERBOARD_MODULE_ENABLED", False):
        return None
    # Intentionally empty until a rankings product ships.
    return None


def build_future_modules(*, user_id: Any = None) -> FutureModules:
    """Typed future_modules block attached to GET /progress/me."""
    enabled = bool(getattr(settings, "PROGRESS_LEADERBOARD_MODULE_ENABLED", False))
    payload = build_leaderboard_module_payload(user_id) if enabled else None
    return FutureModules(
        leaderboard=LeaderboardModuleConfig(
            enabled=enabled,
            reason=(
                "Ready to mount — implement payload builder"
                if enabled
                else "Deferred - personal growth first"
            ),
            version=1,
            mount_point="personal_progress_dashboard",
            api_path="/api/v1/challenges/leaderboard",
            scopes=list(PLANNED_LEADERBOARD_SCOPES),
            payload=payload,
        )
    )
