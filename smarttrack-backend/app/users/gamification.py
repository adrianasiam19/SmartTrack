"""XP / rank / daily challenge streak helpers shared by Phase challenges and other flows."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

# Cumulative XP thresholds to enter each rank (matches frontend XpGauge).
RANK_THRESHOLDS: list[tuple[str, int]] = [
    ("Elite Challenger", 1850),
    ("Gold", 850),
    ("Silver", 350),
    ("Bronze", 100),
    ("Beginner", 0),
]

STREAK_LAST_DATE_KEY = "streak_last_date"


def rank_for_xp(xp: int) -> str:
    total = max(0, int(xp or 0))
    for name, minimum in RANK_THRESHOLDS:
        if total >= minimum:
            return name
    return "Beginner"


def apply_xp(user, delta: int) -> tuple[int, str, int]:
    """
    Add XP to user, refresh rank. Returns (xp_earned, new_rank, user_xp).
    """
    earned = max(0, int(delta or 0))
    if earned:
        user.xp = max(0, (user.xp or 0) + earned)
    user.rank = rank_for_xp(user.xp or 0)
    return earned, user.rank, user.xp or 0


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


def _parse_iso_date(raw: Any) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def record_daily_challenge_streak(user) -> dict[str, Any]:
    """
    Credit one calendar day of challenge activity toward the profile streak.

    Rules (UTC calendar day):
      - Already credited today → no change
      - Last credit was yesterday → streak += 1
      - Never credited / gap ≥ 2 days → streak = 1

    Stores last credit date in learner_profile.streak_last_date.
    """
    today = _today_utc()
    profile = user.learner_profile if isinstance(user.learner_profile, dict) else {}
    profile = dict(profile)
    last = _parse_iso_date(profile.get(STREAK_LAST_DATE_KEY))
    current = int(user.streak or 0)

    if last == today:
        return {
            "streak": current,
            "incremented": False,
            "already_counted_today": True,
            "streak_last_date": today.isoformat(),
        }

    if last == today - timedelta(days=1):
        new_streak = max(1, current + 1)
        incremented = True
    else:
        # First activity ever, or streak broken after a missed day
        new_streak = 1
        incremented = True

    user.streak = new_streak
    profile[STREAK_LAST_DATE_KEY] = today.isoformat()
    # Track personal best streak for the Progress Dashboard
    longest = int(profile.get("longest_streak") or 0)
    profile["longest_streak"] = max(longest, new_streak)
    user.learner_profile = profile
    try:
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(user, "learner_profile")
    except Exception:
        pass

    return {
        "streak": new_streak,
        "incremented": incremented,
        "already_counted_today": False,
        "streak_last_date": today.isoformat(),
    }
