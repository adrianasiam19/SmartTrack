"""Phase / Level API routes."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.phases import service
from app.phases.schemas import (
    CompleteSessionResponse,
    PrefetchStatusResponse,
    ProgressionMeResponse,
    SessionStatusResponse,
    StartLevelResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    WarmPrefetchResponse,
)
from app.users.models import User

router = APIRouter(prefix="/phases", tags=["Phases"])


@router.get("/me", response_model=ProgressionMeResponse)
async def progression_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    data = await service.get_progression(db, current_user.id)
    return data


@router.post("/levels/{level_id}/start", response_model=StartLevelResponse)
async def start_level(
    level_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.start_level(db, current_user.id, level_id, replay=False)


@router.post("/levels/{level_id}/replay", response_model=StartLevelResponse)
async def replay_level(
    level_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.start_level(db, current_user.id, level_id, replay=True)


@router.post("/levels/{level_id}/prefetch", response_model=PrefetchStatusResponse)
async def prefetch_level(
    level_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate the next level's questions in the background while the learner plays."""
    return await service.prefetch_level(db, current_user.id, level_id)


@router.get("/levels/{level_id}/prefetch-status", response_model=PrefetchStatusResponse)
async def prefetch_level_status(
    level_id: int,
    current_user: User = Depends(get_current_user),
):
    return await service.prefetch_status(current_user.id, level_id)


@router.post("/prefetch/warm", response_model=WarmPrefetchResponse)
async def warm_prefetch_buffer(
    anchor_level_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Top up the rolling challenge buffer (next ~2–3 levels) in the background.

    Call from Dashboard / Challenges so Start Level can claim prepared questions.
    """
    return await service.warm_prefetch_buffer(
        db, current_user.id, anchor_level_id=anchor_level_id
    )


@router.get("/prefetch/buffer", response_model=PrefetchStatusResponse)
async def prefetch_buffer_status(
    current_user: User = Depends(get_current_user),
):
    from app.phases.prefetch import phase_prefetch_manager

    return await phase_prefetch_manager.buffer_status(current_user.id)


@router.get("/sessions/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_session_status(db, current_user.id, session_id)


@router.post("/sessions/{session_id}/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    session_id: int,
    body: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.submit_answer(
        db,
        current_user.id,
        session_id,
        body.question_id,
        body.answer,
        body.time_taken_seconds,
    )


@router.post("/sessions/{session_id}/complete", response_model=CompleteSessionResponse)
async def complete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.complete_session(db, current_user.id, session_id)
