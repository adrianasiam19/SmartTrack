"""Pydantic schemas for Personal Progress (Stages 1–5)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PersonalProgressStats(BaseModel):
    """Core personal learning statistics (no peer comparison)."""

    current_phase: int | None = None
    current_phase_name: str | None = None
    current_level: int | None = None
    total_xp: int = 0
    rank: str = "Beginner"
    challenges_completed: int = 0
    learning_topics_completed: int = 0
    current_streak_days: int = 0
    longest_streak_days: int = 0
    overall_accuracy_pct: float | None = None
    recommendations_unlocked: int = 0
    psychometric_completed: bool = False
    wassce_uploaded: bool = False


class WeeklyProgressSummary(BaseModel):
    """Activity since the start of the current UTC calendar week (Monday)."""

    week_start: str  # ISO date
    week_end: str  # ISO date (today)
    challenges_completed: int = 0
    learning_topics_studied: int = 0
    xp_earned: int = 0
    xp_goal: int = 150
    accuracy_pct: float | None = None
    learning_streak_days: int = 0


class ProgressMeter(BaseModel):
    """Single visual progress indicator (bar / ring / counter)."""

    id: str
    label: str
    current: float
    target: float
    pct: float = Field(ge=0, le=100)
    unit: str = ""
    detail: str | None = None


class ProgressVisualizations(BaseModel):
    """Stage 2 progress visuals — personal only, no peer comparison."""

    xp_progress: ProgressMeter
    phase_progress: ProgressMeter
    level_completion: ProgressMeter
    challenge_accuracy: ProgressMeter
    learning_streak: ProgressMeter


class NextGoal(BaseModel):
    """Stage 3 — one personalized objective for the learner right now."""

    id: str
    title: str = "Next Goal"
    message: str
    reason: str | None = None
    priority: int = 100
    progress_current: float | None = None
    progress_target: float | None = None
    progress_pct: float | None = None
    action_label: str | None = None
    action_href: str | None = None


class MotivationalInsight(BaseModel):
    """Stage 4 — supportive, personalized encouragement."""

    id: str
    message: str
    tone: str = "encouragement"  # encouragement | milestone | consistency | growth
    priority: int = 100


class LeaderboardModuleConfig(BaseModel):
    """
    Stage 5 — extension contract for an optional future leaderboard.

    Disabled in MVP. When enabled, frontend ProgressExtensionSlot mounts
    at `mount_point` and may render `payload` without changing Stages 1–4.
    """

    enabled: bool = False
    reason: str = "Deferred - personal growth first"
    version: int = 1
    mount_point: str = "personal_progress_dashboard"
    api_path: str = "/api/v1/challenges/leaderboard"
    scopes: list[str] = Field(
        default_factory=lambda: ["global", "school", "weekly", "monthly", "friends"]
    )
    payload: dict | None = None


class FutureModules(BaseModel):
    """Pluggable modules that can extend the Progress Dashboard later."""

    leaderboard: LeaderboardModuleConfig = Field(
        default_factory=LeaderboardModuleConfig
    )


class PersonalProgressResponse(BaseModel):
    """
    Personal Progress payload.

    Stage 1: stats
    Stage 2: weekly_summary + visualizations
    Stage 3: next_goal
    Stage 4: insights
    Stage 5: future_modules (leaderboard slot — disabled by default)
    """

    stats: PersonalProgressStats
    weekly_summary: WeeklyProgressSummary | None = None
    visualizations: ProgressVisualizations | None = None
    next_goal: NextGoal | None = None
    insights: list[MotivationalInsight] = Field(default_factory=list)
    future_modules: FutureModules = Field(default_factory=FutureModules)
