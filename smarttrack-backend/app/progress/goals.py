"""Dynamic Next Goal selection for the Personal Progress Dashboard (Stage 3)."""
from __future__ import annotations

from datetime import date
from typing import Any

from app.progress.schemas import NextGoal, PersonalProgressStats, WeeklyProgressSummary
from app.users.gamification import STREAK_LAST_DATE_KEY


def _streak_credited_today(profile: dict[str, Any], today: date) -> bool:
    raw = profile.get(STREAK_LAST_DATE_KEY)
    if not raw:
        return False
    try:
        return date.fromisoformat(str(raw)[:10]) == today
    except ValueError:
        return False


def pick_next_goal(
    *,
    stats: PersonalProgressStats,
    weekly: WeeklyProgressSummary,
    profile: dict[str, Any],
    today: date,
    phase_done: int,
    phase_total: int,
    levels_remaining: int,
    phase_eligible_for_recs: bool,
    next_rank_name: str | None,
    xp_to_next_rank: int | None,
) -> NextGoal:
    """
    Choose one personalized objective from the learner's current state.

    Priority favors high-impact unlocks (recommendations, uploads), then
    consistency (streak), then weekly targets and soft growth nudges.
    """
    phase_name = stats.current_phase_name or (
        f"Phase {stats.current_phase}" if stats.current_phase else "your current phase"
    )
    streak_today = _streak_credited_today(profile, today)
    xp_needed_weekly = max(0, int(weekly.xp_goal) - int(weekly.xp_earned))

    candidates: list[NextGoal] = []

    # 1) Psychometric incomplete
    if not stats.psychometric_completed:
        candidates.append(
            NextGoal(
                id="psychometric",
                message="Complete your psychometric assessment to strengthen your learner profile.",
                reason="Psychometric insights improve how Atlas understands your strengths.",
                priority=10,
                action_label="Open Challenges",
                action_href="/challenges",
            )
        )

    # 2) Not started challenges yet
    if stats.challenges_completed == 0 and phase_done == 0:
        candidates.append(
            NextGoal(
                id="start_challenges",
                message="Start Phase 1 challenges to begin your Atlas learning path.",
                reason="Your first completed level unlocks adaptive progression.",
                priority=20,
                progress_current=0,
                progress_target=float(max(phase_total, 1)),
                progress_pct=0,
                action_label="Start Challenges",
                action_href="/challenges",
            )
        )

    # 3) Eligible for recommendations but missing WASSCE upload
    if phase_eligible_for_recs and not stats.wassce_uploaded:
        candidates.append(
            NextGoal(
                id="upload_wassce",
                message="Upload your WASSCE results to unlock programme recommendations.",
                reason="You've completed a phase — academic results unlock personalised programmes.",
                priority=30,
                action_label="Upload Results",
                action_href="/recommendations",
            )
        )

    # 4) Eligible + uploaded, but no recommendation generated yet
    if (
        phase_eligible_for_recs
        and stats.wassce_uploaded
        and stats.recommendations_unlocked == 0
    ):
        candidates.append(
            NextGoal(
                id="generate_recommendations",
                message="Generate your programme recommendations — you're ready.",
                reason="Phase complete and results uploaded. Get your personalised matches.",
                priority=35,
                action_label="Get Recommendations",
                action_href="/recommendations",
            )
        )

    # 5) Finish current phase for recommendation unlock
    if not phase_eligible_for_recs and levels_remaining > 0:
        if levels_remaining <= 3:
            msg = (
                f"Complete {levels_remaining} more level"
                f"{'s' if levels_remaining != 1 else ''} to unlock "
                f"{phase_name} recommendations."
            )
        else:
            msg = (
                f"Complete the remaining levels in {phase_name} "
                "to receive your next recommendation."
            )
        candidates.append(
            NextGoal(
                id="finish_phase_levels",
                message=msg,
                reason=f"{phase_done} of {phase_total} levels done in {phase_name}.",
                priority=40,
                progress_current=float(phase_done),
                progress_target=float(max(phase_total, 1)),
                progress_pct=round(
                    100.0 * phase_done / max(phase_total, 1), 1
                ),
                action_label="Continue Challenges",
                action_href="/challenges",
            )
        )

    # 6) Maintain streak
    if stats.current_streak_days > 0 and not streak_today:
        candidates.append(
            NextGoal(
                id="maintain_streak",
                message="Complete today's challenges to maintain your learning streak.",
                reason=f"You're on a {stats.current_streak_days}-day streak — keep it alive.",
                priority=50,
                progress_current=float(stats.current_streak_days),
                progress_target=float(stats.current_streak_days + 1),
                progress_pct=round(
                    100.0 * stats.current_streak_days / (stats.current_streak_days + 1),
                    1,
                ),
                action_label="Keep Streak Going",
                action_href="/challenges",
            )
        )

    # 7) Start a streak
    if stats.current_streak_days == 0:
        candidates.append(
            NextGoal(
                id="start_streak",
                message="Complete a challenge today to start your learning streak.",
                reason="Consistency compounds — one session starts the habit.",
                priority=55,
                action_label="Start Today",
                action_href="/challenges",
            )
        )

    # 8) Weekly XP goal
    if xp_needed_weekly > 0:
        candidates.append(
            NextGoal(
                id="weekly_xp",
                message=f"Earn {xp_needed_weekly} more XP to reach your weekly goal.",
                reason=f"{weekly.xp_earned} / {weekly.xp_goal} XP earned this week.",
                priority=60,
                progress_current=float(weekly.xp_earned),
                progress_target=float(weekly.xp_goal),
                progress_pct=round(
                    min(100.0, 100.0 * weekly.xp_earned / max(weekly.xp_goal, 1)),
                    1,
                ),
                action_label="Earn XP",
                action_href="/challenges",
            )
        )

    # 9) Learning Center today / first lesson
    if stats.learning_topics_completed == 0:
        candidates.append(
            NextGoal(
                id="first_learning_topic",
                message="Study 1 Learning Center topic to strengthen your learner profile.",
                reason="Lessons improve recommendation quality over time.",
                priority=65,
                action_label="Open Learning Center",
                action_href="/learning",
            )
        )
    elif weekly.learning_topics_studied == 0:
        candidates.append(
            NextGoal(
                id="study_topic_today",
                message="Study 1 Learning Center topic today.",
                reason="A short lesson keeps your weekly learning momentum going.",
                priority=70,
                action_label="Study a Topic",
                action_href="/learning",
            )
        )

    # 10) Next rank nudge
    if next_rank_name and xp_to_next_rank and xp_to_next_rank > 0:
        candidates.append(
            NextGoal(
                id="next_rank",
                message=f"Earn {xp_to_next_rank} more XP to reach {next_rank_name}.",
                reason="Climb your personal rank ladder — no competition required.",
                priority=80,
                action_label="Earn XP",
                action_href="/challenges",
            )
        )

    # 11) Soft default
    candidates.append(
        NextGoal(
            id="keep_progressing",
            message="Keep going! Every completed challenge improves your recommendation quality.",
            reason="Steady personal progress is what Atlas is built for.",
            priority=100,
            action_label="Continue Learning",
            action_href="/challenges",
        )
    )

    candidates.sort(key=lambda g: g.priority)
    return candidates[0]
