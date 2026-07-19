"""XP / rank helpers shared by Phase challenges and other flows."""
from __future__ import annotations

# Cumulative XP thresholds to enter each rank (matches frontend XpGauge).
RANK_THRESHOLDS: list[tuple[str, int]] = [
    ("Elite Challenger", 1850),
    ("Gold", 850),
    ("Silver", 350),
    ("Bronze", 100),
    ("Beginner", 0),
]


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
