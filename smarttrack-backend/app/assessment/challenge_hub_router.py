"""
challenge_hub_router.py — legacy Challenge Hub API (410 Gone).

Phase/Level progression lives under /api/v1/phases.
Routes are kept so older clients get a clear migration signal.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.users.models import User

router = APIRouter(prefix="/challenge-hub", tags=["Challenge Hub"])

_PHASE_GONE = (
    "Challenge Hub is replaced by Phase/Level progression. "
    "Use /api/v1/phases instead."
)


def _gone() -> None:
    raise HTTPException(status_code=410, detail=_PHASE_GONE)


class StartChallengeRequest(BaseModel):
    challenge_level: int = 1


class SubmitAnswerRequest(BaseModel):
    session_id: str
    subject: str
    question_index: int
    user_answer: str
    time_taken_seconds: float


class SubjectQuestionsRequest(BaseModel):
    session_id: str
    subject_index: Optional[int] = None


class CompleteSessionRequest(BaseModel):
    session_id: str


class ContinueLevelRequest(BaseModel):
    session_id: str


@router.post("/start")
async def start_challenge(
    body: StartChallengeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deprecated — use POST /phases/levels/{level_id}/start."""
    _gone()


@router.post("/questions")
async def get_questions(
    body: SubjectQuestionsRequest,
    current_user: User = Depends(get_current_user),
):
    """Deprecated — use Phase session APIs."""
    _gone()


@router.post("/submit")
async def submit_challenge_answer(
    body: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deprecated — use POST /phases/sessions/{id}/submit-answer."""
    _gone()


@router.post("/complete")
async def complete_challenge_session(
    body: CompleteSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deprecated — use POST /phases/sessions/{id}/complete."""
    _gone()


@router.post("/continue")
async def continue_challenge(
    body: ContinueLevelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deprecated — Phase levels unlock sequentially via /phases."""
    _gone()


@router.get("/summary")
async def get_summary(
    session_id: str = Query(..., description="The session ID"),
    current_user: User = Depends(get_current_user),
):
    """Deprecated — session results come from Phase complete."""
    _gone()
