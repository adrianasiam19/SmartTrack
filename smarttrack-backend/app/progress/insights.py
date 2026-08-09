"""Personalized motivational insights for the Progress Dashboard (Stage 4)."""
from __future__ import annotations

from app.progress.schemas import (
    MotivationalInsight,
    PersonalProgressStats,
    WeeklyProgressSummary,
)


def build_motivational_insights(
    *,
    stats: PersonalProgressStats,
    weekly: WeeklyProgressSummary,
    levels_remaining: int,
    phase_eligible_for_recs: bool,
    phase_name: str,
    limit: int = 3,
) -> list[MotivationalInsight]:
    """
    Build supportive, personalized messages from the learner's own progress.

    No peer comparison. Ordered by relevance; capped at `limit`.
    """
    items: list[MotivationalInsight] = []

    # Near recommendation unlock
    if not phase_eligible_for_recs and levels_remaining == 1:
        items.append(
            MotivationalInsight(
                id="one_level_away",
                message=(
                    f"You're only one level away from unlocking your next "
                    f"recommendation in {phase_name}."
                ),
                tone="milestone",
                priority=10,
            )
        )
    elif not phase_eligible_for_recs and 1 < levels_remaining <= 3:
        items.append(
            MotivationalInsight(
                id="close_to_unlock",
                message=(
                    f"You're close — {levels_remaining} levels left in "
                    f"{phase_name} before your next recommendation unlock."
                ),
                tone="milestone",
                priority=15,
            )
        )

    # Accuracy improved this week vs overall
    if (
        weekly.accuracy_pct is not None
        and stats.overall_accuracy_pct is not None
        and weekly.accuracy_pct > stats.overall_accuracy_pct + 0.5
        and weekly.challenges_completed > 0
    ):
        items.append(
            MotivationalInsight(
                id="accuracy_improved",
                message="Your challenge accuracy has improved this week. That's real growth.",
                tone="growth",
                priority=20,
            )
        )
    elif stats.overall_accuracy_pct is not None and stats.overall_accuracy_pct >= 80:
        items.append(
            MotivationalInsight(
                id="strong_accuracy",
                message=(
                    f"Strong work — you're holding {stats.overall_accuracy_pct:.0f}% "
                    "challenge accuracy. Keep refining mastery."
                ),
                tone="growth",
                priority=25,
            )
        )

    # Streak consistency
    if stats.current_streak_days >= 7:
        items.append(
            MotivationalInsight(
                id="streak_strong",
                message=(
                    f"Impressive consistency — a {stats.current_streak_days}-day "
                    "learning streak. You're building a lasting habit."
                ),
                tone="consistency",
                priority=30,
            )
        )
    elif stats.current_streak_days >= 2:
        items.append(
            MotivationalInsight(
                id="streak_alive",
                message="You're doing great! Keep your learning streak alive.",
                tone="consistency",
                priority=35,
            )
        )
    elif stats.current_streak_days == 1:
        items.append(
            MotivationalInsight(
                id="streak_started",
                message="Nice start — come back tomorrow to grow your learning streak.",
                tone="consistency",
                priority=40,
            )
        )

    # Weekly activity wins
    if weekly.challenges_completed > 0:
        items.append(
            MotivationalInsight(
                id="challenges_this_week",
                message=(
                    f"Excellent work! You've completed {weekly.challenges_completed} "
                    f"challenge{'s' if weekly.challenges_completed != 1 else ''} this week."
                ),
                tone="milestone",
                priority=45,
            )
        )

    if weekly.learning_topics_studied > 0:
        items.append(
            MotivationalInsight(
                id="learning_this_week",
                message=(
                    f"You studied {weekly.learning_topics_studied} Learning Center "
                    f"topic{'s' if weekly.learning_topics_studied != 1 else ''} this week. "
                    "That deepens your profile."
                ),
                tone="growth",
                priority=50,
            )
        )

    if weekly.xp_earned >= weekly.xp_goal:
        items.append(
            MotivationalInsight(
                id="weekly_xp_met",
                message="You've hit your weekly XP goal. Consistent effort pays off.",
                tone="milestone",
                priority=22,
            )
        )
    elif weekly.xp_earned > 0:
        items.append(
            MotivationalInsight(
                id="weekly_xp_progress",
                message=(
                    f"You've earned +{weekly.xp_earned} XP this week — "
                    "every session moves you forward."
                ),
                tone="encouragement",
                priority=55,
            )
        )

    # Personal best streak
    if (
        stats.current_streak_days > 0
        and stats.current_streak_days >= stats.longest_streak_days
        and stats.longest_streak_days >= 3
    ):
        items.append(
            MotivationalInsight(
                id="personal_best_streak",
                message="You're matching your longest learning streak. Keep the momentum.",
                tone="milestone",
                priority=28,
            )
        )

    # Recommendations / profile completeness
    if phase_eligible_for_recs and stats.wassce_uploaded:
        items.append(
            MotivationalInsight(
                id="recs_ready",
                message=(
                    "You've unlocked the path to programme recommendations. "
                    "Your progress is working for you."
                ),
                tone="milestone",
                priority=18,
            )
        )
    elif stats.recommendations_unlocked > 0:
        items.append(
            MotivationalInsight(
                id="recs_unlocked",
                message=(
                    "Keep going! Every completed challenge improves your "
                    "recommendation quality."
                ),
                tone="encouragement",
                priority=48,
            )
        )

    # Soft defaults so the panel is never empty for active learners
    if stats.challenges_completed > 0 or stats.learning_topics_completed > 0:
        items.append(
            MotivationalInsight(
                id="consistent_progress",
                message="You're making consistent progress. Keep learning!",
                tone="encouragement",
                priority=90,
            )
        )
    else:
        items.append(
            MotivationalInsight(
                id="welcome_journey",
                message=(
                    "Welcome to your personal growth path. "
                    "Start a challenge — Atlas adapts as you learn."
                ),
                tone="encouragement",
                priority=95,
            )
        )

    # Deduplicate by id, sort, cap
    seen: set[str] = set()
    unique: list[MotivationalInsight] = []
    for item in sorted(items, key=lambda x: x.priority):
        if item.id in seen:
            continue
        seen.add(item.id)
        unique.append(item)
        if len(unique) >= limit:
            break
    return unique
