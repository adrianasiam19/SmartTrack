"""Authenticated, level-scoped Learning Center API."""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assessment.models import CurriculumLesson
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.learning.service import (
    AI_CONTENT_VERSION,
    TutorUnavailable,
    answer_lesson_question,
    generate_ai_lesson,
)
from app.users.models import User

router = APIRouter(prefix="/learning", tags=["Learning Center"])

SUPPORTED_LEVELS = {"SHS 1", "SHS 2"}
PROGRAMME_MAP = {"General Science": "Science", "General Arts": "Arts"}


class TopicResponse(BaseModel):
    curriculum_id: str
    title: str
    subject: str
    shs_level: str
    estimated_minutes: int
    difficulty: int
    xp_reward: int


class WorkedExample(BaseModel):
    title: str
    steps: list[str]
    answer: str


class AITaughtLesson(BaseModel):
    topic_title: str
    simple_introduction: str
    main_explanation: str
    step_by_step_examples: list[WorkedExample]
    real_life_applications: list[str]
    important_points: list[str]
    common_mistakes: list[str]
    short_summary: str


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


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _scope_for(user: User) -> tuple[str, str]:
    if user.shs_level not in SUPPORTED_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The AI Learning Center is available only for SHS 1 and SHS 2.",
        )
    programme = PROGRAMME_MAP.get(user.programme or "")
    if not programme:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Complete your SHS programme setup before opening the Learning Center.",
        )
    return user.shs_level, programme


def _is_in_scope(
    lesson: CurriculumLesson, shs_level: str, programme: str
) -> bool:
    return (
        shs_level in (lesson.shs_levels or [])
        and lesson.programme in {"Both", programme}
    )


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


async def _get_scoped_lesson(
    curriculum_id: str,
    user: User,
    db: AsyncSession,
) -> tuple[CurriculumLesson, str]:
    shs_level, programme = _scope_for(user)
    result = await db.execute(
        select(CurriculumLesson).where(
            CurriculumLesson.curriculum_id == curriculum_id
        )
    )
    lesson = result.scalar_one_or_none()
    if lesson is None or not _is_in_scope(lesson, shs_level, programme):
        # A generic 404 prevents leaking the existence of another level's lesson.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found in your curriculum.",
        )
    return lesson, shs_level


@router.get("/topics", response_model=list[TopicResponse])
async def search_topics(
    query: str = Query(default="", max_length=150),
    subject: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=20, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search only the authenticated student's official curriculum."""
    shs_level, programme = _scope_for(user)
    result = await db.execute(select(CurriculumLesson))
    lessons = [
        lesson
        for lesson in result.scalars().all()
        if _is_in_scope(lesson, shs_level, programme)
        and (not subject or lesson.subject.lower() == subject.lower())
    ]

    normalised_query = _normalise(query)
    ranked = [
        (_search_score(normalised_query, lesson), lesson) for lesson in lessons
    ]
    if normalised_query:
        ranked = [item for item in ranked if item[0] >= 0.48]
    ranked.sort(key=lambda item: (-item[0], item[1].subject, item[1].title))

    return [
        TopicResponse(
            curriculum_id=lesson.curriculum_id,
            title=lesson.title,
            subject=lesson.subject,
            shs_level=shs_level,
            estimated_minutes=lesson.estimated_minutes,
            difficulty=lesson.difficulty,
            xp_reward=lesson.xp_reward,
        )
        for _, lesson in ranked[:limit]
    ]


@router.post("/lessons/{curriculum_id}/teach", response_model=LessonResponse)
async def teach_lesson(
    curriculum_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a DB lesson first, then return its cached or newly AI-taught form."""
    curriculum, shs_level = await _get_scoped_lesson(curriculum_id, user, db)
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
        await db.flush()

    return LessonResponse(
        curriculum_id=curriculum.curriculum_id,
        subject=curriculum.subject,
        shs_level=shs_level,
        estimated_minutes=curriculum.estimated_minutes,
        xp_reward=curriculum.xp_reward,
        lesson=taught_lesson,
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
    """Answer a follow-up using the server-retrieved curriculum lesson."""
    curriculum, shs_level = await _get_scoped_lesson(curriculum_id, user, db)
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
