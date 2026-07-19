"""
daily_streak.py
────────────────
Router for Daily Streak / Today's Challenge system.

Endpoints:
  GET    /daily-streak/progress          → Get progress for all 4 subjects (legacy)
  POST   /daily-streak/progress          → Update progress for a specific subject/level (legacy)
  GET    /daily-streak/todays-challenge  → Get today's mixed challenge composition
"""
import hashlib
import random
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assessment.models import DailyStreakProgress
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.users.models import User

router = APIRouter(prefix="/daily-streak", tags=["Daily Streak"])

# ── Schemas ──────────────────────────────────────────────────────────────────

SUBJECT_IDS = [
    "core-mathematics",
    "integrated-science",
    "english-language",
    "social-studies",
]

SUBJECT_LABELS: dict[str, str] = {
    "core-mathematics": "Mathematics",
    "integrated-science": "Science",
    "english-language": "English",
    "social-studies": "Social Studies",
}

SUBJECT_COLORS: dict[str, str] = {
    "core-mathematics": "#2563EB",
    "integrated-science": "#059669",
    "english-language": "#7C3AED",
    "social-studies": "#D97706",
}


class LevelProgressOut(BaseModel):
    level_id: int
    progress: int
    completed: bool
    locked: bool


class SubjectProgressOut(BaseModel):
    subject_id: str
    levels: list[LevelProgressOut]


class DailyStreakProgressResponse(BaseModel):
    subjects: list[SubjectProgressOut]
    total_xp_earned: int


class UpdateProgressRequest(BaseModel):
    subject_id: str
    level_id: int
    progress: int  # 0–100
    completed: bool = False


class UpdateProgressResponse(BaseModel):
    success: bool
    message: str
    subject: SubjectProgressOut
    xp_earned: int = 0
    streak_updated: bool = False


class ChallengeSection(BaseModel):
    """One subject section within today's mixed challenge."""
    subject_id: str
    label: str
    color: str
    question_count: int
    level_id: int  # 1, 2, or 3 — hidden from student


class TodaysChallengeResponse(BaseModel):
    """The mixed challenge configuration for today."""
    challenge_id: str
    date: str
    sections: list[ChallengeSection]
    total_questions: int
    xp_reward: int
    current_streak: int
    current_xp: int


# ── Helpers ──────────────────────────────────────────────────────────────────

def _default_levels() -> list[dict]:
    """Return the default 3-level structure for any subject."""
    return [
        {"level_id": 1, "progress": 0, "completed": False, "locked": False},
        {"level_id": 2, "progress": 0, "completed": False, "locked": True},
        {"level_id": 3, "progress": 0, "completed": False, "locked": True},
    ]


async def _get_or_create_progress(
    db: AsyncSession, user_id, subject_id: str
) -> dict:
    """Get the progress dict for a subject, initializing from DB rows or defaults."""
    result = await db.execute(
        select(DailyStreakProgress)
        .where(DailyStreakProgress.user_id == user_id)
        .where(DailyStreakProgress.subject_id == subject_id)
    )
    rows = result.scalars().all()

    if not rows:
        # No rows yet — return default locked structure
        levels = _default_levels()
        return {"subject_id": subject_id, "levels": levels}

    # Build levels from DB rows
    level_map: dict[int, dict] = {}
    for row in rows:
        level_map[row.level_id] = {
            "level_id": row.level_id,
            "progress": row.progress,
            "completed": row.completed,
            "locked": False,  # Was started, so not locked
        }

    # Fill in any missing levels
    default_levels = _default_levels()
    result_levels = []
    for dl in default_levels:
        lid = dl["level_id"]
        if lid in level_map:
            result_levels.append(level_map[lid])
        else:
            result_levels.append(dl)

    # Determine lock state: level N+1 is unlocked only if level N is completed
    for i in range(1, len(result_levels)):
        prev = result_levels[i - 1]
        if not prev["completed"]:
            result_levels[i]["locked"] = True
        else:
            result_levels[i]["locked"] = False

    return {"subject_id": subject_id, "levels": result_levels}


def _todays_seed() -> str:
    """Generate a daily seed string based on the date."""
    today = date.today()
    return f"atlas-challenge-{today.isoformat()}"


def _determine_challenge_composition() -> list[dict]:
    """
    Determine today's challenge composition deterministically from the date.
    Each day has a different mix of subjects and question counts.
    """
    seed_str = _todays_seed()
    seed_int = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16)
    rng = random.Random(seed_int)

    # Base configuration: 4 subjects, each with 3-5 questions
    subjects = list(SUBJECT_IDS)
    rng.shuffle(subjects)

    # Vary question counts per subject (3-6 questions each)
    sections = []
    for subject_id in subjects:
        count = rng.randint(3, 6)
        level_id = 1  # Start at level 1, progress behind the scenes
        sections.append({
            "subject_id": subject_id,
            "question_count": count,
            "level_id": level_id,
        })

    return sections


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.get("/progress", response_model=DailyStreakProgressResponse)
async def get_daily_streak_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the user's progress across all 4 daily streak subjects (legacy)."""
    subjects = []
    total_xp = current_user.xp or 0

    for sid in SUBJECT_IDS:
        subj = await _get_or_create_progress(db, current_user.id, sid)
        subjects.append(SubjectProgressOut(**subj))

    return DailyStreakProgressResponse(subjects=subjects, total_xp_earned=total_xp)


@router.post("/progress", response_model=UpdateProgressResponse)
async def update_daily_streak_progress(
    body: UpdateProgressRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update progress for a specific subject/level. Completing a level unlocks the next."""
    if body.subject_id not in SUBJECT_IDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid subject_id. Must be one of: {', '.join(SUBJECT_IDS)}",
        )
    if not (0 <= body.progress <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progress must be between 0 and 100.",
        )

    # Fetch or create the row for this subject + level
    result = await db.execute(
        select(DailyStreakProgress)
        .where(DailyStreakProgress.user_id == current_user.id)
        .where(DailyStreakProgress.subject_id == body.subject_id)
        .where(DailyStreakProgress.level_id == body.level_id)
    )
    row = result.scalar_one_or_none()

    xp_earned = 0
    streak_updated = False

    if row is None:
        row = DailyStreakProgress(
            user_id=current_user.id,
            subject_id=body.subject_id,
            level_id=body.level_id,
            progress=body.progress,
            completed=body.completed,
            started_at=datetime.now(timezone.utc),
        )
        db.add(row)
    else:
        old_completed = row.completed
        row.progress = body.progress
        row.completed = body.completed
        if not old_completed and body.completed:
            row.completed_at = datetime.now(timezone.utc)

    await db.flush()

    if body.completed:
        from app.users.gamification import apply_xp

        level_xp_map = {1: 100, 2: 150, 3: 200}
        xp_reward = level_xp_map.get(body.level_id, 100)
        xp_earned, _rank, _user_xp = apply_xp(current_user, xp_reward)
        current_user.streak = (current_user.streak or 0) + 1
        streak_updated = True
        await db.flush()

    await db.commit()

    subj = await _get_or_create_progress(db, current_user.id, body.subject_id)

    return UpdateProgressResponse(
        success=True,
        message="Progress updated.",
        subject=SubjectProgressOut(**subj),
        xp_earned=xp_earned,
        streak_updated=streak_updated,
    )


@router.get("/todays-challenge", response_model=TodaysChallengeResponse)
async def get_todays_challenge(
    current_user: User = Depends(get_current_user),
):
    """
    Get today's mixed challenge composition.

    Returns a daily-varying mix of subjects with question counts.
    The challenge composition changes each day automatically.
    Students see a unified challenge instead of choosing subjects.
    Level progression (1→2→3) happens behind the scenes.
    """
    sections_data = _determine_challenge_composition()

    # Calculate total questions and XP reward
    total_questions = sum(s["question_count"] for s in sections_data)
    base_xp_per_question = 10
    xp_reward = total_questions * base_xp_per_question

    # Build challenge ID from date
    challenge_id = f"challenge-{date.today().isoformat()}"

    challenge_sections = [
        ChallengeSection(
            subject_id=s["subject_id"],
            label=SUBJECT_LABELS.get(s["subject_id"], s["subject_id"]),
            color=SUBJECT_COLORS.get(s["subject_id"], "#64748B"),
            question_count=s["question_count"],
            level_id=s["level_id"],
        )
        for s in sections_data
    ]

    return TodaysChallengeResponse(
        challenge_id=challenge_id,
        date=date.today().isoformat(),
        sections=challenge_sections,
        total_questions=total_questions,
        xp_reward=xp_reward,
        current_streak=current_user.streak or 0,
        current_xp=current_user.xp or 0,
    )
