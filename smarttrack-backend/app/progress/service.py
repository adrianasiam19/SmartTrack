"""Aggregate personal progress from existing Atlas data sources."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.assessment.models import ChallengeResponse, ChallengeSession
from app.notifications.models import Notification
from app.phases.models import Level, Phase, UserLevelProgress, UserPhaseProgress
from app.progress.future_modules import build_future_modules
from app.progress.goals import pick_next_goal
from app.progress.insights import build_motivational_insights
from app.progress.schemas import (
    PersonalProgressResponse,
    PersonalProgressStats,
    ProgressMeter,
    ProgressVisualizations,
    WeeklyProgressSummary,
)
from app.recommendations.models import Recommendation
from app.users.gamification import RANK_THRESHOLDS
from app.users.models import AcademicRecord, User

LONGEST_STREAK_KEY = "longest_streak"
COMPLETED_LESSONS_LOG_KEY = "completed_lessons_log"
WEEKLY_XP_GOAL = 150
STREAK_MILESTONES = (3, 7, 14, 30, 60, 100)


def _week_bounds_utc(today: date | None = None) -> tuple[datetime, datetime, date, date]:
    """Return (week_start_dt, now_dt, week_start_date, today_date) in UTC. Week starts Monday."""
    now = datetime.now(timezone.utc)
    today = today or now.date()
    week_start_date = today - timedelta(days=today.weekday())  # Monday
    week_start_dt = datetime(
        week_start_date.year,
        week_start_date.month,
        week_start_date.day,
        tzinfo=timezone.utc,
    )
    return week_start_dt, now, week_start_date, today


def _clamp_pct(current: float, target: float) -> float:
    if target <= 0:
        return 100.0 if current > 0 else 0.0
    return round(min(100.0, max(0.0, 100.0 * current / target)), 1)


def _next_rank_target(xp: int) -> tuple[str | None, int, int]:
    """
    Return (next_rank_name, xp_into_current_band, band_size).
    Band is from current rank floor to next rank floor.
    """
    total = max(0, int(xp or 0))
    # RANK_THRESHOLDS is high→low; reverse for ascending floors
    ascending = list(reversed(RANK_THRESHOLDS))  # Beginner..Elite
    current_floor = 0
    next_name: str | None = None
    next_floor: int | None = None
    for i, (name, minimum) in enumerate(ascending):
        if total >= minimum:
            current_floor = minimum
            if i + 1 < len(ascending):
                next_name, next_floor = ascending[i + 1]
            else:
                next_name, next_floor = None, None
    if next_floor is None:
        # Max rank — show full bar within elite band
        return None, total, max(total, 1)
    into = total - current_floor
    span = max(1, next_floor - current_floor)
    return next_name, into, span


def _next_streak_milestone(current: int) -> int:
    for m in STREAK_MILESTONES:
        if current < m:
            return m
    return max(STREAK_MILESTONES[-1], current + 7)


def _count_lessons_in_week(profile: dict[str, Any], week_start: date, today: date) -> int:
    log = profile.get(COMPLETED_LESSONS_LOG_KEY) or []
    if not isinstance(log, list):
        return 0
    count = 0
    for entry in log:
        if isinstance(entry, dict):
            raw = entry.get("at") or entry.get("completed_at")
        else:
            continue
        if not raw:
            continue
        try:
            d = date.fromisoformat(str(raw)[:10])
        except ValueError:
            continue
        if week_start <= d <= today:
            count += 1
    return count


def _xp_from_lesson_log(profile: dict[str, Any], week_start: date, today: date) -> int:
    log = profile.get(COMPLETED_LESSONS_LOG_KEY) or []
    if not isinstance(log, list):
        return 0
    total = 0
    for entry in log:
        if not isinstance(entry, dict):
            continue
        raw = entry.get("at") or entry.get("completed_at")
        if not raw:
            continue
        try:
            d = date.fromisoformat(str(raw)[:10])
        except ValueError:
            continue
        if week_start <= d <= today:
            total += int(entry.get("xp") or 0)
    return total


async def build_personal_progress(
    db: AsyncSession,
    user: User,
) -> PersonalProgressResponse:
    user_id = user.id
    profile: dict[str, Any] = (
        dict(user.learner_profile) if isinstance(user.learner_profile, dict) else {}
    )
    week_start_dt, now_dt, week_start_date, today = _week_bounds_utc()

    # Keep phase/level rows in sync with /phases/me so greeting never invents Phase 3.
    from app.phases.service import ensure_user_progression

    await ensure_user_progression(db, user_id)

    # ── Phase / level ─────────────────────────────────────────────────────
    phases = (
        await db.execute(
            select(Phase).options(selectinload(Phase.levels)).order_by(Phase.number)
        )
    ).scalars().all()
    level_prog = {
        p.level_id: p
        for p in (
            await db.execute(
                select(UserLevelProgress).where(UserLevelProgress.user_id == user_id)
            )
        ).scalars().all()
    }
    phase_prog = {
        p.phase_id: p
        for p in (
            await db.execute(
                select(UserPhaseProgress).where(UserPhaseProgress.user_id == user_id)
            )
        ).scalars().all()
    }

    current_phase: int | None = None
    current_phase_name: str | None = None
    current_level: int | None = None
    current_phase_obj: Phase | None = None

    for phase in phases:
        upp = phase_prog.get(phase.id)
        status = (upp.status if upp else "locked") or "locked"
        if status == "completed" or status == "locked":
            continue
        levels = sorted(phase.levels, key=lambda L: L.number)
        pick: Level | None = None
        for level in levels:
            lp = level_prog.get(level.id)
            st = (lp.status if lp else "locked") or "locked"
            if st == "in_progress":
                pick = level
                break
        if pick is None:
            for level in levels:
                lp = level_prog.get(level.id)
                st = (lp.status if lp else "locked") or "locked"
                if st in ("available", "in_progress"):
                    pick = level
                    break
        # Never pick locked levels as "current".
        if pick is not None or status in ("in_progress", "available"):
            current_phase = phase.number
            current_phase_name = phase.name
            current_level = pick.number if pick else None
            current_phase_obj = phase
            break

    if current_phase is None and phases:
        # All done → last phase; otherwise first unlocked/available, else Phase 1.
        all_done = all(
            ((phase_prog.get(p.id).status if phase_prog.get(p.id) else None) or "")
            == "completed"
            for p in phases
        )
        if all_done:
            pick_phase = phases[-1]
            pick_level = (
                max(phases[-1].levels, key=lambda L: L.number)
                if phases[-1].levels
                else None
            )
        else:
            pick_phase = next(
                (
                    p
                    for p in phases
                    if ((phase_prog.get(p.id).status if phase_prog.get(p.id) else None) or "")
                    in ("available", "in_progress")
                ),
                phases[0],
            )
            pick_level = None
            for level in sorted(pick_phase.levels, key=lambda L: L.number):
                st = (
                    (level_prog.get(level.id).status if level_prog.get(level.id) else None)
                    or "locked"
                )
                if st in ("available", "in_progress"):
                    pick_level = level
                    break
        current_phase = pick_phase.number
        current_phase_name = pick_phase.name
        current_phase_obj = pick_phase
        current_level = pick_level.number if pick_level else None

    # Level completion totals
    all_levels = [L for ph in phases for L in ph.levels]
    total_levels = len(all_levels) or 1
    completed_levels = sum(
        1
        for L in all_levels
        if ((level_prog.get(L.id).status if level_prog.get(L.id) else None) or "")
        == "completed"
    )

    phase_levels = list(current_phase_obj.levels) if current_phase_obj else []
    phase_total = len(phase_levels) or 1
    phase_done = sum(
        1
        for L in phase_levels
        if ((level_prog.get(L.id).status if level_prog.get(L.id) else None) or "")
        == "completed"
    )

    # ── Challenges completed (finished sessions) ──────────────────────────
    challenges_completed = int(
        (
            await db.execute(
                select(func.count())
                .select_from(ChallengeSession)
                .where(
                    ChallengeSession.user_id == user_id,
                    ChallengeSession.status == "completed",
                )
            )
        ).scalar_one()
        or 0
    )

    # ── Accuracy from answered challenge responses ────────────────────────
    answered = (
        await db.execute(
            select(
                func.count().filter(ChallengeResponse.is_correct.is_not(None)),
                func.count().filter(ChallengeResponse.is_correct.is_(True)),
            ).where(ChallengeResponse.user_id == user_id)
        )
    ).one()
    total_answered = int(answered[0] or 0)
    total_correct = int(answered[1] or 0)
    accuracy: float | None = None
    if total_answered > 0:
        accuracy = round(100.0 * total_correct / total_answered, 1)

    # ── Learning Center ───────────────────────────────────────────────────
    completed_lessons = profile.get("completed_lessons") or []
    if not isinstance(completed_lessons, list):
        completed_lessons = []
    learning_topics = len(completed_lessons)

    # ── Streaks ───────────────────────────────────────────────────────────
    current_streak = int(user.streak or 0)
    longest = int(profile.get(LONGEST_STREAK_KEY) or 0)
    longest = max(longest, current_streak)

    # ── Recommendations ───────────────────────────────────────────────────
    rec_count = int(
        (
            await db.execute(
                select(func.count())
                .select_from(Recommendation)
                .where(Recommendation.user_id == user_id)
            )
        ).scalar_one()
        or 0
    )

    # ── Psychometric ──────────────────────────────────────────────────────
    psycho_done = bool(user.starter_arena_completed) or bool(
        profile.get("psychometric_completed")
        or profile.get("psychometric_checkpoint_completed")
    )
    if not psycho_done:
        pool = profile.get("assessment_pool") or profile.get("psychometric_responses")
        if isinstance(pool, list) and len(pool) > 0:
            psycho_done = True
        elif isinstance(pool, dict) and (
            pool.get("psychometric_responses") or pool.get("psychometric_shown")
        ):
            psycho_done = True

    # ── WASSCE / academic upload ──────────────────────────────────────────
    academic_count = int(
        (
            await db.execute(
                select(func.count())
                .select_from(AcademicRecord)
                .where(AcademicRecord.user_id == user_id)
            )
        ).scalar_one()
        or 0
    )
    upload = profile.get("academic_upload") or profile.get("wassce") or {}
    upload_confirmed = (
        isinstance(upload, dict)
        and upload.get("confirmed") is not False
        and (upload.get("grades") or upload.get("grades_extracted"))
    )
    wassce_uploaded = bool(
        academic_count > 0
        or profile.get("wassce_uploaded")
        or profile.get("academic_results_uploaded")
        or upload_confirmed
    )

    stats = PersonalProgressStats(
        current_phase=current_phase,
        current_phase_name=current_phase_name,
        current_level=current_level,
        total_xp=int(user.xp or 0),
        rank=str(user.rank or "Beginner"),
        challenges_completed=challenges_completed,
        learning_topics_completed=learning_topics,
        current_streak_days=current_streak,
        longest_streak_days=longest,
        overall_accuracy_pct=accuracy,
        recommendations_unlocked=rec_count,
        psychometric_completed=psycho_done,
        wassce_uploaded=wassce_uploaded,
    )

    # ── Stage 2: Weekly summary ───────────────────────────────────────────
    week_challenges = int(
        (
            await db.execute(
                select(func.count())
                .select_from(ChallengeSession)
                .where(
                    ChallengeSession.user_id == user_id,
                    ChallengeSession.status == "completed",
                    ChallengeSession.completed_at.is_not(None),
                    ChallengeSession.completed_at >= week_start_dt,
                    ChallengeSession.completed_at <= now_dt,
                )
            )
        ).scalar_one()
        or 0
    )

    week_xp_challenges = int(
        (
            await db.execute(
                select(func.coalesce(func.sum(ChallengeSession.total_xp), 0)).where(
                    ChallengeSession.user_id == user_id,
                    ChallengeSession.status == "completed",
                    ChallengeSession.completed_at.is_not(None),
                    ChallengeSession.completed_at >= week_start_dt,
                    ChallengeSession.completed_at <= now_dt,
                )
            )
        ).scalar_one()
        or 0
    )

    week_answered = (
        await db.execute(
            select(
                func.count().filter(ChallengeResponse.is_correct.is_not(None)),
                func.count().filter(ChallengeResponse.is_correct.is_(True)),
            ).where(
                ChallengeResponse.user_id == user_id,
                func.coalesce(
                    ChallengeResponse.answered_at,
                    ChallengeResponse.created_at,
                )
                >= week_start_dt,
            )
        )
    ).one()
    week_total_ans = int(week_answered[0] or 0)
    week_correct = int(week_answered[1] or 0)
    week_accuracy: float | None = None
    if week_total_ans > 0:
        week_accuracy = round(100.0 * week_correct / week_total_ans, 1)

    week_lessons = _count_lessons_in_week(profile, week_start_date, today)
    week_xp_lessons = _xp_from_lesson_log(profile, week_start_date, today)

    # Fallback: lesson_completed notifications this week (covers older completions)
    if week_lessons == 0 or week_xp_lessons == 0:
        notif_rows = (
            await db.execute(
                select(Notification.data).where(
                    Notification.user_id == user_id,
                    Notification.created_at >= week_start_dt,
                    Notification.created_at <= now_dt,
                )
            )
        ).scalars().all()
        lesson_notifs = [
            d
            for d in notif_rows
            if isinstance(d, dict) and d.get("event") == "lesson_completed"
        ]
        if week_lessons == 0:
            week_lessons = len(lesson_notifs)
        if week_xp_lessons == 0:
            week_xp_lessons = sum(int(d.get("xp_earned") or 0) for d in lesson_notifs)

    week_xp = int(week_xp_challenges) + int(week_xp_lessons)

    weekly = WeeklyProgressSummary(
        week_start=week_start_date.isoformat(),
        week_end=today.isoformat(),
        challenges_completed=week_challenges,
        learning_topics_studied=week_lessons,
        xp_earned=week_xp,
        xp_goal=WEEKLY_XP_GOAL,
        accuracy_pct=week_accuracy,
        learning_streak_days=current_streak,
    )

    # ── Stage 2: Visualizations ───────────────────────────────────────────
    next_rank, xp_into, xp_span = _next_rank_target(stats.total_xp)
    xp_detail = (
        f"{int(xp_into)} / {xp_span} XP toward {next_rank}"
        if next_rank
        else "Top rank reached — keep earning XP"
    )
    streak_target = _next_streak_milestone(current_streak)

    visualizations = ProgressVisualizations(
        xp_progress=ProgressMeter(
            id="xp",
            label="XP Progress",
            current=float(xp_into),
            target=float(xp_span),
            pct=_clamp_pct(xp_into, xp_span) if next_rank else 100.0,
            unit="XP",
            detail=xp_detail,
        ),
        phase_progress=ProgressMeter(
            id="phase",
            label="Phase Progress",
            current=float(phase_done),
            target=float(phase_total),
            pct=_clamp_pct(phase_done, phase_total),
            unit="levels",
            detail=(
                f"{phase_done} of {phase_total} levels in "
                f"{current_phase_name or f'Phase {current_phase or 1}'}"
            ),
        ),
        level_completion=ProgressMeter(
            id="levels",
            label="Level Completion",
            current=float(completed_levels),
            target=float(total_levels),
            pct=_clamp_pct(completed_levels, total_levels),
            unit="levels",
            detail=f"{completed_levels} of {total_levels} levels across all phases",
        ),
        challenge_accuracy=ProgressMeter(
            id="accuracy",
            label="Challenge Accuracy",
            current=float(accuracy or 0),
            target=100.0,
            pct=float(accuracy or 0),
            unit="%",
            detail=(
                f"{accuracy}% overall"
                if accuracy is not None
                else "Complete challenges to see accuracy"
            ),
        ),
        learning_streak=ProgressMeter(
            id="streak",
            label="Learning Streak",
            current=float(current_streak),
            target=float(streak_target),
            pct=_clamp_pct(current_streak, streak_target),
            unit="days",
            detail=(
                f"{current_streak}-day streak · next milestone {streak_target} days"
                if current_streak > 0
                else "Complete a challenge today to start a streak"
            ),
        ),
    )

    # ── Stage 3: Next Goal ────────────────────────────────────────────────
    phase_eligible = any(
        sum(
            1
            for L in ph.levels
            if ((level_prog.get(L.id).status if level_prog.get(L.id) else None) or "")
            == "completed"
        )
        == len(ph.levels)
        and len(ph.levels) > 0
        for ph in phases
    )
    levels_remaining = max(0, phase_total - phase_done)
    xp_to_next = None
    if next_rank:
        xp_to_next = max(0, int(xp_span - xp_into))

    next_goal = pick_next_goal(
        stats=stats,
        weekly=weekly,
        profile=profile,
        today=today,
        phase_done=phase_done,
        phase_total=phase_total,
        levels_remaining=levels_remaining,
        phase_eligible_for_recs=phase_eligible,
        next_rank_name=next_rank,
        xp_to_next_rank=xp_to_next,
    )

    # ── Stage 4: Motivational insights ────────────────────────────────────
    insights = build_motivational_insights(
        stats=stats,
        weekly=weekly,
        levels_remaining=levels_remaining,
        phase_eligible_for_recs=phase_eligible,
        phase_name=current_phase_name
        or (f"Phase {current_phase}" if current_phase else "your current phase"),
        limit=3,
    )

    return PersonalProgressResponse(
        stats=stats,
        weekly_summary=weekly,
        visualizations=visualizations,
        next_goal=next_goal,
        insights=insights,
        future_modules=build_future_modules(user_id=user_id),
    )
