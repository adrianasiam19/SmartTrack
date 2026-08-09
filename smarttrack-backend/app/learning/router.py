"""Authenticated Learning Center API — phase-independent digital library."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.assessment.models import CurriculumLesson
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.learning.service import (
    AI_CONTENT_VERSION,
    CHALLENGE_SUBJECT_TO_CURRICULUM,
    TutorUnavailable,
    answer_lesson_question,
    generate_ai_lesson,
    generate_explore_source,
    resolve_explore_subject,
    _slugify_topic,
)
from app.phases.models import UserSubjectPerformance
from app.users.gamification import apply_xp
from app.users.models import User

router = APIRouter(prefix="/learning", tags=["Learning Center"])

# Soft AI depth preference only — never used to hide catalogue content
LEVEL_PREFERENCE = {"SHS 1", "SHS 2", "SHS 3"}

POPULAR_FALLBACK_IDS = [
    "coremath-m1t1",
    "eng-lang-s5t1",
    "int-sci-s1t1",
    "soc-st-s1t1",
    "bio-2-s4t1",
]


class TopicResponse(BaseModel):
    curriculum_id: str
    title: str
    subject: str
    shs_level: str = ""
    estimated_minutes: int
    difficulty: int
    xp_reward: int
    reason: str | None = None


class WorkedExample(BaseModel):
    title: str
    steps: list[str]
    answer: str


class VisualAidPublic(BaseModel):
    """Learner-facing visual only — no attribution, source, or license."""

    url: str
    alt: str | None = None
    concept: str | None = None
    requires_labels: bool | None = None
    legend: str | None = None


class AITaughtLesson(BaseModel):
    topic_title: str
    simple_introduction: str
    main_explanation: str
    step_by_step_examples: list[WorkedExample]
    real_life_applications: list[str]
    important_points: list[str]
    common_mistakes: list[str]
    short_summary: str
    visual_aid: VisualAidPublic | None = None


class LessonResponse(BaseModel):
    curriculum_id: str
    subject: str
    shs_level: str
    estimated_minutes: int
    xp_reward: int
    lesson: AITaughtLesson


class TutorMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4_000)


class TutorRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2_000)
    history: list[TutorMessage] = Field(default_factory=list, max_length=20)


class TutorResponse(BaseModel):
    response: str


class LibraryHomeResponse(BaseModel):
    continue_learning: TopicResponse | None = None
    recommended: list[TopicResponse] = Field(default_factory=list)
    recent: list[TopicResponse] = Field(default_factory=list)
    bookmarks: list[TopicResponse] = Field(default_factory=list)


class BookmarkToggleResponse(BaseModel):
    curriculum_id: str
    bookmarked: bool
    bookmarks: list[TopicResponse]


class RelatedTopicsResponse(BaseModel):
    topics: list[TopicResponse]


class LearningResourceItem(BaseModel):
    """Optional supplementary resource (video today; pdf/simulation later)."""

    id: str
    kind: Literal["video", "pdf", "simulation", "animation", "link"]
    title: str
    url: str
    provider: str
    thumbnail_url: str | None = None
    channel: str | None = None
    duration_seconds: int | None = None
    description: str | None = None
    query: str | None = None
    extra: dict[str, Any] | None = None


class LessonResourcesResponse(BaseModel):
    curriculum_id: str
    queries: list[str] = Field(default_factory=list)
    resources: list[LearningResourceItem] = Field(default_factory=list)


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _soft_level(user: User, lesson: CurriculumLesson | None = None) -> str:
    """Prefer profile level for AI tone; fall back to lesson levels or SHS 2."""
    if user.shs_level in LEVEL_PREFERENCE:
        if lesson and lesson.shs_levels and user.shs_level not in lesson.shs_levels:
            return lesson.shs_levels[0]
        return user.shs_level
    if lesson and lesson.shs_levels:
        return lesson.shs_levels[0]
    return "SHS 2"


def _search_score(query: str, lesson: CurriculumLesson) -> float:
    if not query:
        return 1.0
    title = _normalise(lesson.title)
    searchable = _normalise(lesson.search_text)
    if query == title:
        return 1.0
    if query in title:
        return 0.96
    if query in searchable:
        return 0.82

    title_ratio = SequenceMatcher(None, query, title).ratio()
    query_words = query.split()
    searchable_words = set(searchable.split())
    keyword_coverage = (
        sum(word in searchable_words for word in query_words) / max(1, len(query_words))
    )
    candidate_words = title.split()
    word_scores = [
        max(
            (SequenceMatcher(None, word, candidate).ratio() for candidate in candidate_words),
            default=0.0,
        )
        for word in query_words
    ]
    word_score = sum(word_scores) / max(1, len(word_scores))
    return max(title_ratio, word_score * 0.9, keyword_coverage * 0.8)


def _topic_from_lesson(
    lesson: CurriculumLesson, *, reason: str | None = None, shs_level: str = ""
) -> TopicResponse:
    return TopicResponse(
        curriculum_id=lesson.curriculum_id,
        title=lesson.title,
        subject=lesson.subject,
        shs_level=shs_level,
        estimated_minutes=lesson.estimated_minutes,
        difficulty=lesson.difficulty,
        xp_reward=lesson.xp_reward,
        reason=reason,
    )


def _profile_dict(user: User) -> dict[str, Any]:
    return dict(user.learner_profile or {})


def _entries_to_topics(
    entries: list[dict[str, Any]],
    by_id: dict[str, CurriculumLesson],
) -> list[TopicResponse]:
    """Only return topics that still exist in the curriculum catalogue."""
    out: list[TopicResponse] = []
    for entry in entries:
        cid = str(entry.get("curriculum_id") or "")
        lesson = by_id.get(cid)
        if lesson:
            out.append(_topic_from_lesson(lesson))
    return out


async def _get_lesson(
    curriculum_id: str,
    db: AsyncSession,
) -> CurriculumLesson:
    result = await db.execute(
        select(CurriculumLesson).where(CurriculumLesson.curriculum_id == curriculum_id)
    )
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found.",
        )
    return lesson


async def _lessons_by_id(db: AsyncSession) -> dict[str, CurriculumLesson]:
    result = await db.execute(select(CurriculumLesson))
    return {L.curriculum_id: L for L in result.scalars().all()}


def _touch_recent(profile: dict[str, Any], lesson: CurriculumLesson) -> None:
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "curriculum_id": lesson.curriculum_id,
        "title": lesson.title,
        "subject": lesson.subject,
        "visited_at": now,
        "estimated_minutes": lesson.estimated_minutes,
        "difficulty": lesson.difficulty,
        "xp_reward": lesson.xp_reward,
    }
    recent = [
        e
        for e in list(profile.get("learning_recent") or [])
        if e.get("curriculum_id") != lesson.curriculum_id
    ]
    recent.insert(0, entry)
    profile["learning_recent"] = recent[:20]
    profile["last_opened_topic"] = entry


def profile_completed(user: User) -> list[str]:
    profile = _profile_dict(user)
    return list(profile.get("completed_lessons") or [])


async def _build_recommended(
    user: User,
    db: AsyncSession,
    by_id: dict[str, CurriculumLesson],
    *,
    exclude: set[str],
) -> list[TopicResponse]:
    """Rank topics from challenge subject performance, then fill with catalogue."""
    picks: list[TopicResponse] = []
    seen: set[str] = set(exclude)
    completed = set(profile_completed(user))

    perf_rows = (
        await db.execute(
            select(UserSubjectPerformance).where(UserSubjectPerformance.user_id == user.id)
        )
    ).scalars().all()

    # Weaker subjects first; still include any subject the learner has attempted
    ordered = sorted(
        perf_rows,
        key=lambda p: (
            p.weak_level_streak or 0,
            1.0 - float(p.rolling_accuracy if p.rolling_accuracy is not None else 0.5),
        ),
        reverse=True,
    )

    for perf in ordered:
        curriculum_subject = CHALLENGE_SUBJECT_TO_CURRICULUM.get(perf.subject)
        if not curriculum_subject:
            continue
        accuracy = float(
            perf.rolling_accuracy if perf.rolling_accuracy is not None else 0.5
        )
        candidates = [
            L
            for L in by_id.values()
            if L.subject == curriculum_subject
            and L.curriculum_id not in seen
            and L.curriculum_id not in completed
        ]
        candidates.sort(key=lambda L: (L.difficulty, L.title))
        for lesson in candidates[:2]:
            if (perf.weak_level_streak or 0) >= 1 or accuracy < 0.7:
                reason = f"From Challenges — strengthen {curriculum_subject}"
            else:
                reason = f"From Challenges — keep practising {curriculum_subject}"
            picks.append(_topic_from_lesson(lesson, reason=reason))
            seen.add(lesson.curriculum_id)
            if len(picks) >= 6:
                return picks

    # One topic per subject as cold-start / fill (works even with no challenge history)
    for subject in (
        "Core Mathematics",
        "English Language",
        "Integrated Science",
        "Social Studies",
        "Biology",
        "Chemistry",
        "Physics",
        "Additional Mathematics",
    ):
        if len(picks) >= 6:
            break
        candidates = [
            L
            for L in by_id.values()
            if L.subject == subject
            and L.curriculum_id not in seen
            and L.curriculum_id not in completed
        ]
        if not candidates:
            continue
        candidates.sort(key=lambda L: (L.difficulty, L.title))
        lesson = candidates[0]
        picks.append(_topic_from_lesson(lesson, reason="Great place to start"))
        seen.add(lesson.curriculum_id)

    for cid in POPULAR_FALLBACK_IDS:
        if len(picks) >= 6:
            break
        if cid in seen or cid in completed:
            continue
        lesson = by_id.get(cid)
        if lesson:
            picks.append(_topic_from_lesson(lesson, reason="Popular starting topic"))
            seen.add(cid)

    if len(picks) < 6:
        for lesson in sorted(by_id.values(), key=lambda L: (L.difficulty, L.title)):
            if lesson.curriculum_id in seen or lesson.curriculum_id in completed:
                continue
            picks.append(_topic_from_lesson(lesson, reason="Explore this topic"))
            seen.add(lesson.curriculum_id)
            if len(picks) >= 6:
                break

    return picks


@router.get("/search", response_model=list[TopicResponse])
async def unified_search(
    q: str | None = Query(default=None, max_length=150),
    query: str | None = Query(default=None, max_length=150),
    subject: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=20, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search the full curriculum — not filtered by phase or SHS level."""
    _ = user
    search_text = (q or query or "").strip()
    result = await db.execute(select(CurriculumLesson))
    lessons = list(result.scalars().all())
    if subject:
        lessons = [L for L in lessons if L.subject.lower() == subject.lower()]

    normalised_query = _normalise(search_text)
    ranked = [(_search_score(normalised_query, lesson), lesson) for lesson in lessons]
    if normalised_query:
        ranked = [item for item in ranked if item[0] >= 0.40]
    ranked.sort(key=lambda item: (-item[0], item[1].subject, item[1].title))

    return [_topic_from_lesson(lesson) for _, lesson in ranked[:limit]]


@router.get("/topics", response_model=list[TopicResponse])
async def list_or_search_topics(
    query: str = Query(default="", max_length=150),
    subject: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=100, ge=1, le=250),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List topics (optionally by subject) across the full library."""
    return await unified_search(
        q=query or None,
        query=None,
        subject=subject,
        limit=limit,
        user=user,
        db=db,
    )


class ExploreTopicRequest(BaseModel):
    query: str = Field(min_length=2, max_length=150)
    subject: str | None = Field(default=None, max_length=100)


@router.post("/explore", response_model=TopicResponse)
async def explore_topic(
    body: ExploreTopicRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    When catalogue search misses, Atlas AI creates a learnable topic so the
    student can open lesson notes and chat immediately.
    """
    title = body.query.strip()
    if len(title) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enter a topic to explore.",
        )

    matches = await unified_search(
        q=title,
        query=None,
        subject=body.subject,
        limit=5,
        user=user,
        db=db,
    )
    if matches:
        best = matches[0]
        existing = await db.execute(
            select(CurriculumLesson).where(
                CurriculumLesson.curriculum_id == best.curriculum_id
            )
        )
        lesson = existing.scalar_one_or_none()
        if lesson and _search_score(_normalise(title), lesson) >= 0.72:
            return best

    subject = resolve_explore_subject(body.subject, title)
    curriculum_id = f"explore-{_slugify_topic(subject)}-{_slugify_topic(title)}"[:120]

    existing_row = await db.execute(
        select(CurriculumLesson).where(CurriculumLesson.curriculum_id == curriculum_id)
    )
    cached = existing_row.scalar_one_or_none()
    if cached:
        return _topic_from_lesson(cached, reason="Prepared by Atlas AI")

    shs_level = _soft_level(user)
    try:
        source = await generate_explore_source(
            title=title,
            subject=subject,
            shs_level=shs_level,
        )
    except TutorUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Atlas AI could not prepare this topic. Please try again.",
        ) from exc

    search_bits = [
        str(source.get("title") or title),
        subject,
        str(source.get("overview") or ""),
        str(source.get("summary") or ""),
        " ".join(str(x) for x in (source.get("key_concepts") or [])),
        " ".join(str(x) for x in (source.get("explanations") or [])),
    ]
    lesson = CurriculumLesson(
        curriculum_id=curriculum_id,
        title=str(source.get("title") or title).strip()[:500],
        subject=subject,
        programme="Both",
        shs_levels=[shs_level] if shs_level in LEVEL_PREFERENCE else ["SHS 1", "SHS 2"],
        unit_id="atlas-explore",
        difficulty=2,
        estimated_minutes=15,
        xp_reward=35,
        source_content=source,
        search_text=re.sub(r"\s+", " ", " ".join(search_bits)).strip().lower(),
        ai_content_by_level={},
        ai_content_version="v1",
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return _topic_from_lesson(lesson, reason="Prepared by Atlas AI")


@router.get("/library", response_model=LibraryHomeResponse)
async def library_home(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    by_id = await _lessons_by_id(db)
    profile = _profile_dict(user)

    continue_learning = None
    last = profile.get("last_opened_topic")
    if isinstance(last, dict) and last.get("curriculum_id"):
        lesson = by_id.get(str(last["curriculum_id"]))
        if lesson:
            continue_learning = _topic_from_lesson(
                lesson, reason="Continue where you left off"
            )

    recent = _entries_to_topics(list(profile.get("learning_recent") or [])[:8], by_id)
    bookmarks = _entries_to_topics(
        list(profile.get("learning_bookmarks") or [])[:12], by_id
    )

    recommended = await _build_recommended(
        user,
        db,
        by_id,
        exclude={
            *(t.curriculum_id for t in recent),
            *((continue_learning.curriculum_id,) if continue_learning else ()),
        },
    )

    return LibraryHomeResponse(
        continue_learning=continue_learning,
        recommended=recommended,
        recent=recent,
        bookmarks=bookmarks,
    )


@router.post("/lessons/{curriculum_id}/opened", response_model=TopicResponse)
async def mark_opened(
    curriculum_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson = await _get_lesson(curriculum_id, db)
    profile = _profile_dict(user)
    _touch_recent(profile, lesson)
    user.learner_profile = profile
    flag_modified(user, "learner_profile")
    await db.commit()
    return _topic_from_lesson(lesson)


@router.post("/bookmarks/{curriculum_id}/toggle", response_model=BookmarkToggleResponse)
async def toggle_bookmark(
    curriculum_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson = await _get_lesson(curriculum_id, db)
    profile = _profile_dict(user)
    bookmarks = list(profile.get("learning_bookmarks") or [])
    existing = next(
        (i for i, b in enumerate(bookmarks) if b.get("curriculum_id") == curriculum_id),
        None,
    )
    bookmarked = False
    if existing is None:
        bookmarks.insert(
            0,
            {
                "curriculum_id": lesson.curriculum_id,
                "title": lesson.title,
                "subject": lesson.subject,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "estimated_minutes": lesson.estimated_minutes,
                "difficulty": lesson.difficulty,
                "xp_reward": lesson.xp_reward,
            },
        )
        bookmarked = True
    else:
        bookmarks.pop(existing)
    profile["learning_bookmarks"] = bookmarks[:50]
    user.learner_profile = profile
    flag_modified(user, "learner_profile")
    await db.commit()

    all_by_id = await _lessons_by_id(db)
    return BookmarkToggleResponse(
        curriculum_id=curriculum_id,
        bookmarked=bookmarked,
        bookmarks=_entries_to_topics(profile["learning_bookmarks"], all_by_id),
    )


@router.get("/lessons/{curriculum_id}/related", response_model=RelatedTopicsResponse)
async def related_topics(
    curriculum_id: str,
    limit: int = Query(default=6, ge=1, le=12),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _ = user
    lesson = await _get_lesson(curriculum_id, db)
    result = await db.execute(select(CurriculumLesson))
    siblings = [
        L
        for L in result.scalars().all()
        if L.subject == lesson.subject and L.curriculum_id != curriculum_id
    ]
    stem = "-".join(curriculum_id.split("-")[:3])
    siblings.sort(
        key=lambda L: (
            0 if L.curriculum_id.startswith(stem) else 1,
            L.difficulty,
            L.title,
        )
    )
    return RelatedTopicsResponse(
        topics=[_topic_from_lesson(L) for L in siblings[:limit]]
    )


@router.get("/lessons/{curriculum_id}/resources", response_model=LessonResourcesResponse)
async def lesson_resources(
    curriculum_id: str,
    kinds: str = Query(
        default="video",
        description="Comma-separated resource kinds (video, pdf, simulation, animation, link).",
    ),
    limit: int = Query(default=3, ge=1, le=6),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deferred optional learning resources for a lesson (videos first).

    Loaded separately from /teach so the AI lesson can appear immediately.
    """
    lesson = await _get_lesson(curriculum_id, db)
    shs_level = _soft_level(user, lesson)
    wanted = {k.strip().lower() for k in kinds.split(",") if k.strip()}
    resources: list[dict[str, Any]] = []
    queries: list[str] = []

    if "video" in wanted:
        try:
            from app.media.video_retrieval import retrieve_educational_videos
            from app.config import settings as app_settings

            result = await retrieve_educational_videos(
                title=lesson.title,
                subject=lesson.subject,
                shs_level=shs_level,
                limit=limit or int(getattr(app_settings, "EDUCATIONAL_VIDEO_LIMIT", 3)),
            )
            queries = list(result.get("queries") or [])
            resources.extend(result.get("resources") or [])
        except Exception:
            # Optional enrichment — never fail the lesson experience
            pass

    # Future: if "pdf" in wanted / "simulation" in wanted → plug in here.

    return LessonResourcesResponse(
        curriculum_id=curriculum_id,
        queries=queries,
        resources=resources,
    )


@router.post("/lessons/{curriculum_id}/teach", response_model=LessonResponse)
async def teach_lesson(
    curriculum_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a DB lesson, then return cached or newly AI-taught content."""
    curriculum = await _get_lesson(curriculum_id, db)
    shs_level = _soft_level(user, curriculum)

    profile = _profile_dict(user)
    _touch_recent(profile, curriculum)
    user.learner_profile = profile
    flag_modified(user, "learner_profile")

    cache: dict[str, Any] = curriculum.ai_content_by_level or {}
    taught_lesson = (
        cache.get(shs_level)
        if curriculum.ai_content_version == AI_CONTENT_VERSION
        else None
    )

    if not taught_lesson:
        try:
            taught_lesson = await generate_ai_lesson(
                title=curriculum.title,
                subject=curriculum.subject,
                shs_level=shs_level,
                source_content=curriculum.source_content,
            )
        except TutorUnavailable as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Atlas AI could not prepare this lesson. Please try again.",
            ) from exc
        curriculum.ai_content_by_level = {**cache, shs_level: taught_lesson}
        curriculum.ai_content_version = AI_CONTENT_VERSION

    await db.commit()

    from app.media.learner_media import scrub_lesson_for_learner

    public_lesson = scrub_lesson_for_learner(
        taught_lesson if isinstance(taught_lesson, dict) else {}
    )

    return LessonResponse(
        curriculum_id=curriculum.curriculum_id,
        subject=curriculum.subject,
        shs_level=shs_level,
        estimated_minutes=curriculum.estimated_minutes,
        xp_reward=curriculum.xp_reward,
        lesson=public_lesson,
    )


class LessonCompleteResponse(BaseModel):
    curriculum_id: str
    xp_earned: int
    user_xp: int
    rank: str
    already_completed: bool = False


@router.post("/lessons/{curriculum_id}/complete", response_model=LessonCompleteResponse)
async def complete_lesson(
    curriculum_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Award lesson XP once per curriculum id (tracked on learner_profile)."""
    curriculum = await _get_lesson(curriculum_id, db)
    profile = _profile_dict(user)
    completed = list(profile.get("completed_lessons") or [])
    if curriculum_id in completed:
        return LessonCompleteResponse(
            curriculum_id=curriculum_id,
            xp_earned=0,
            user_xp=user.xp or 0,
            rank=user.rank or "Beginner",
            already_completed=True,
        )

    prev_rank = user.rank or "Beginner"
    prev_rank = user.rank or "Beginner"
    xp_earned, rank, user_xp = apply_xp(user, curriculum.xp_reward or 10)
    if rank != prev_rank and rank != "Beginner":
        try:
            from app.notifications.events import notify_badge_unlocked

            await notify_badge_unlocked(db, user.id, rank=rank)
        except Exception:
            import logging

            logging.getLogger(__name__).exception("Failed to create badge notification")
    completed.append(curriculum_id)
    profile["completed_lessons"] = completed[-200:]
    # Timestamped log for Personal Progress weekly summary (Stage 2)
    lesson_log = list(profile.get("completed_lessons_log") or [])
    if not isinstance(lesson_log, list):
        lesson_log = []
    lesson_log.append(
        {
            "id": curriculum_id,
            "at": datetime.now(timezone.utc).isoformat(),
            "xp": int(xp_earned or 0),
        }
    )
    profile["completed_lessons_log"] = lesson_log[-200:]
    user.learner_profile = profile
    flag_modified(user, "learner_profile")

    try:
        from app.notifications.events import notify_lesson_completed

        await notify_lesson_completed(
            db,
            user.id,
            title=curriculum.title,
            subject=curriculum.subject,
            xp_earned=xp_earned,
        )
    except Exception:
        import logging

        logging.getLogger(__name__).exception("Failed to create lesson notification")

    await db.commit()
    return LessonCompleteResponse(
        curriculum_id=curriculum_id,
        xp_earned=xp_earned,
        user_xp=user_xp,
        rank=rank,
        already_completed=False,
    )


@router.post(
    "/lessons/{curriculum_id}/ask",
    response_model=TutorResponse,
)
async def ask_atlas(
    curriculum_id: str,
    body: TutorRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Answer a follow-up using the curriculum lesson (any phase)."""
    curriculum = await _get_lesson(curriculum_id, db)
    shs_level = _soft_level(user, curriculum)
    try:
        response = await answer_lesson_question(
            question=body.message.strip(),
            history=[message.model_dump() for message in body.history],
            title=curriculum.title,
            subject=curriculum.subject,
            shs_level=shs_level,
            source_content=curriculum.source_content,
        )
    except TutorUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Atlas AI is temporarily unavailable. Please try again.",
        ) from exc
    return TutorResponse(response=response)
