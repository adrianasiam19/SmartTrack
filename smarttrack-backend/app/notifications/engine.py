"""Stage 7 — Intelligent Notification Logic.

Evaluates learner activity signals and creates reminder / nudge
notifications with cooldown-based deduplication (rule_key).
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.notifications.activity import get_learner_activity_snapshot
from app.notifications.models import Notification
from app.notifications.service import create_notification
from app.notifications.types import NotificationCategory, NotificationPriority
from app.users.models import User
from app.users.gamification import STREAK_LAST_DATE_KEY, RANK_THRESHOLDS

logger = logging.getLogger(__name__)

ENGINE_LAST_RUN_KEY = "notif_engine_last_run"
ENGINE_MIN_INTERVAL = timedelta(minutes=20)

LEARNING_IDLE_DAYS = 3
STREAK_MILESTONES = (3, 7, 14, 30)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _parse_iso(raw: Any) -> datetime | None:
    if not raw:
        return None
    try:
        text = str(raw).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        return _as_utc(dt)
    except Exception:
        return None


async def has_recent_rule(
    db: AsyncSession,
    user_id,
    rule_key: str,
    *,
    within_hours: float,
) -> bool:
    """True if a notification with this rule_key was created recently."""
    cutoff = _now() - timedelta(hours=within_hours)
    result = await db.execute(
        select(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.created_at >= cutoff,
            Notification.data.is_not(None),
        )
        .order_by(Notification.created_at.desc())
        .limit(40)
    )
    for row in result.scalars().all():
        data = row.data if isinstance(row.data, dict) else {}
        if data.get("rule_key") == rule_key:
            return True
    return False


async def has_any_rule(
    db: AsyncSession,
    user_id,
    rule_key: str,
) -> bool:
    """True if this rule_key was ever emitted (for one-shot milestones)."""
    result = await db.execute(
        select(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.data.is_not(None),
        )
        .order_by(Notification.created_at.desc())
        .limit(120)
    )
    for row in result.scalars().all():
        data = row.data if isinstance(row.data, dict) else {}
        if data.get("rule_key") == rule_key:
            return True
    return False


async def _emit(
    db: AsyncSession,
    user: User,
    *,
    rule_key: str,
    title: str,
    message: str,
    category: NotificationCategory,
    action_link: str,
    priority: str | NotificationPriority = "normal",
    within_hours: float,
    extra: dict[str, Any] | None = None,
    one_shot: bool = False,
) -> bool:
    if one_shot:
        if await has_any_rule(db, user.id, rule_key):
            return False
    elif await has_recent_rule(db, user.id, rule_key, within_hours=within_hours):
        return False

    data = {"rule_key": rule_key, "event": rule_key, "href": action_link}
    if extra:
        data.update(extra)

    await create_notification(
        db,
        user_id=user.id,
        title=title,
        message=message,
        category=category,
        action_link=action_link,
        priority=priority,
        data=data,
    )
    return True


def _should_run_engine(user: User) -> bool:
    profile = user.learner_profile if isinstance(user.learner_profile, dict) else {}
    last = _parse_iso(profile.get(ENGINE_LAST_RUN_KEY))
    if last is None:
        return True
    return (_now() - last) >= ENGINE_MIN_INTERVAL


def _mark_engine_run(user: User) -> None:
    profile = dict(user.learner_profile) if isinstance(user.learner_profile, dict) else {}
    profile[ENGINE_LAST_RUN_KEY] = _now().isoformat()
    user.learner_profile = profile
    flag_modified(user, "learner_profile")


async def run_notification_engine(
    db: AsyncSession,
    user: User,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """
    Evaluate Stage 7 rules and create notifications as needed.

    Safe to call on every notifications list/unread fetch — throttled per user.
    """
    if not force and not _should_run_engine(user):
        return {"ran": False, "created": 0, "rules_fired": []}

    snapshot = await get_learner_activity_snapshot(db, user)
    fired: list[str] = []

    # ── Continue where you left off (exact phase • level) ─────────────────
    continue_point = (snapshot.get("challenge_progress") or {}).get("continue_point")
    if isinstance(continue_point, dict) and continue_point.get("level_number"):
        phase_n = continue_point.get("phase_number") or "?"
        level_n = continue_point.get("level_number")
        label = continue_point.get("label") or f"Continue from Phase {phase_n} • Level {level_n}"
        rule_key = f"continue_phase_{phase_n}_level_{level_n}"
        if await _emit(
            db,
            user,
            rule_key=rule_key,
            title="Continue where you left off",
            message=label,
            category=NotificationCategory.PROGRESS,
            action_link="/challenges",
            priority="high",
            within_hours=36,
            extra={
                "phase_number": phase_n,
                "level_number": level_n,
            },
        ):
            fired.append(rule_key)

    # ── Continue today's challenges ───────────────────────────────────────
    profile = user.learner_profile if isinstance(user.learner_profile, dict) else {}
    streak_last = str(profile.get(STREAK_LAST_DATE_KEY) or "")[:10]
    today = _now().date().isoformat()
    has_challenge_progress = int(
        (snapshot.get("challenge_progress") or {}).get("levels_completed") or 0
    ) > 0 or bool(continue_point)
    if has_challenge_progress and streak_last != today:
        if await _emit(
            db,
            user,
            rule_key="continue_todays_challenges",
            title="Continue today's challenges",
            message="Jump back into Challenges and keep your progress moving today.",
            category=NotificationCategory.REMINDER,
            action_link="/challenges",
            priority="normal",
            within_hours=20,
        ):
            fired.append("continue_todays_challenges")

    # ── Learning Center idle nudge ────────────────────────────────────────
    learning = snapshot.get("learning_center_activity") or {}
    last_visit = _parse_iso(learning.get("last_visited_at"))
    lessons_done = int(learning.get("completed_lesson_count") or 0)
    idle_enough = False
    if last_visit is None:
        # Never visited — nudge after account has had time to explore
        created = _as_utc(user.created_at) or _now()
        idle_enough = (_now() - created) >= timedelta(days=LEARNING_IDLE_DAYS)
    else:
        idle_enough = (_now() - last_visit) >= timedelta(days=LEARNING_IDLE_DAYS)

    if idle_enough:
        msg = (
            "Visit the Learning Center today to strengthen your subjects."
            if lessons_done == 0
            else "It's been a few days — open the Learning Center and continue studying."
        )
        if await _emit(
            db,
            user,
            rule_key="learning_center_idle",
            title="Visit the Learning Center today",
            message=msg,
            category=NotificationCategory.LEARNING,
            action_link="/learning",
            priority="normal",
            within_hours=72,
        ):
            fired.append("learning_center_idle")

    # ── Recommendations available (safety net if event missed) ────────────
    rec = snapshot.get("recommendation_eligibility") or {}
    if rec.get("eligible"):
        if await _emit(
            db,
            user,
            rule_key="recommendations_available",
            title="Recommendations are now available",
            message=(
                "Your programme recommendations are unlocked. "
                "Open Recommendations to review them."
            ),
            category=NotificationCategory.RECOMMENDATION,
            action_link="/recommendations",
            priority="high",
            within_hours=168,  # weekly
            extra={"eligible": True},
        ):
            fired.append("recommendations_available")

    # ── WASSCE upload nudge ───────────────────────────────────────────────
    wassce = snapshot.get("wassce_upload_status") or {}
    shs = (getattr(user, "shs_level", None) or "").strip()
    should_prompt_wassce = (
        not wassce.get("uploaded")
        and (
            bool(rec.get("eligible"))
            or shs in {"SHS 3", "Completed SHS"}
        )
    )
    if should_prompt_wassce:
        if await _emit(
            db,
            user,
            rule_key="wassce_upload_nudge",
            title="Upload your WASSCE results",
            message=(
                "Upload your WASSCE / academic results to unlock stronger "
                "programme recommendations."
            ),
            category=NotificationCategory.REMINDER,
            action_link="/recommendations",
            priority="normal",
            within_hours=120,
        ):
            fired.append("wassce_upload_nudge")

    # ── Keep streak alive ─────────────────────────────────────────────────
    streak = int(snapshot.get("current_learning_streak") or 0)
    if streak > 0 and streak_last and streak_last != today:
        # At risk of breaking if they don't act today
        yesterday = (_now().date() - timedelta(days=1)).isoformat()
        if streak_last == yesterday or streak_last < yesterday:
            if await _emit(
                db,
                user,
                rule_key="keep_streak_alive",
                title="Keep your learning streak alive",
                message=(
                    f"You're on a {streak}-day streak. Complete a challenge today "
                    "so it doesn't reset."
                ),
                category=NotificationCategory.STREAK,
                action_link="/challenges",
                priority="high",
                within_hours=18,
                extra={"streak": streak},
            ):
                fired.append("keep_streak_alive")

    # ── Streak milestone celebration (one-shot per milestone) ──────────────
    if streak in STREAK_MILESTONES:
        rule_key = f"streak_milestone_{streak}"
        if await _emit(
            db,
            user,
            rule_key=rule_key,
            title="Streak milestone!",
            message=f"Amazing — you've kept a {streak}-day learning streak.",
            category=NotificationCategory.STREAK,
            action_link="/dashboard",
            priority="high",
            within_hours=24,
            one_shot=True,
            extra={"streak": streak},
        ):
            fired.append(rule_key)

    # ── Rank / badge celebration (if never notified for current rank) ──────
    rank = (snapshot.get("achievement_milestones") or {}).get("rank") or user.rank
    if rank and rank != "Beginner":
        rule_key = f"badge_unlocked_{str(rank).lower().replace(' ', '_')}"
        threshold = next((m for name, m in RANK_THRESHOLDS if name == rank), None)
        msg = f"Badge unlocked: {rank}."
        if threshold is not None:
            msg = f"Badge unlocked: you've reached {rank} ({threshold}+ XP)."
        if await _emit(
            db,
            user,
            rule_key=rule_key,
            title="Badge unlocked",
            message=msg,
            category=NotificationCategory.ACHIEVEMENT,
            action_link="/dashboard",
            priority="high",
            within_hours=24,
            one_shot=True,
            extra={"rank": rank, "badge": rank},
        ):
            fired.append(rule_key)

    _mark_engine_run(user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Notification engine commit failed for user=%s", user.id)
        return {"ran": True, "created": 0, "rules_fired": []}

    return {"ran": True, "created": len(fired), "rules_fired": fired}


async def notify_return_after_absence(
    db: AsyncSession,
    user: User,
    *,
    previous_login: datetime | None,
) -> bool:
    """
    Stage 7 rule: if learner has not logged in for 24+ hours, remind them
    to continue learning. Called from auth before last_login is overwritten.
    """
    if previous_login is None:
        return False
    prev = _as_utc(previous_login)
    if prev is None:
        return False
    if (_now() - prev) < timedelta(hours=24):
        return False

    created = await _emit(
        db,
        user,
        rule_key="return_after_24h",
        title="Welcome back",
        message="It's been a while — continue learning where you left off.",
        category=NotificationCategory.REMINDER,
        action_link="/dashboard",
        priority="high",
        within_hours=24,
    )
    if created:
        try:
            await db.flush()
        except Exception:
            logger.exception("Failed to flush return-after-absence notification")
            return False
    return created
