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
    ProgressionMeResponse,
    StartLevelResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
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
