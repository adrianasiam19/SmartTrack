"""
challenge_hub_router.py — Atlas Adaptive Challenge Hub API

Endpoints:
  POST /challenge-hub/start       — Start a new challenge session
  GET  /challenge-hub/questions   — Get questions for current/next subject
  POST /challenge-hub/submit      — Submit an answer
  GET  /challenge-hub/summary     — Get session summary
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.assessment.challenge_hub import (
    start_challenge_session,
    get_current_questions,
    get_current_subject_index,
    submit_answer,
    complete_session,
    get_session_summary,
    CORE_SUBJECTS,
)
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/challenge-hub", tags=["Challenge Hub"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class StartChallengeRequest(BaseModel):
    challenge_level: int = 1  # 1 = Easy, 2 = Moderate, 3 = Difficult

    class Config:
        json_schema_extra = {
            "example": {"challenge_level": 1}
        }


class SubmitAnswerRequest(BaseModel):
    session_id: str
    subject: str
    question_index: int
    user_answer: str
    time_taken_seconds: float


class SubjectQuestionsRequest(BaseModel):
    session_id: str
    subject_index: Optional[int] = None  # None = current subject


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/start")
async def start_challenge(
    body: StartChallengeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start a new Challenge Hub session.

    Generates 6 questions for each of the 4 Core Subjects (24 total)
    using the connected LLM, adapted to the student's SHS level and
    selected challenge level (1 = Easy, 2 = Moderate, 3 = Difficult).
    Falls back to hardcoded questions if AI is unavailable.
    """
    if body.challenge_level not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="challenge_level must be 1, 2, or 3")

    shs_level = current_user.shs_level or "SHS 1"

    session_data = await start_challenge_session(
        db=db,
        user_id=current_user.id,
        shs_level=shs_level,
        challenge_level=body.challenge_level,
    )

    if not session_data or not session_data.get("questions"):
        raise HTTPException(status_code=500, detail="Failed to generate challenge questions")

    return {
        "success": True,
        "session": session_data,
    }


@router.post("/questions")
async def get_questions(
    body: SubjectQuestionsRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Get questions for a specific subject within a session.

    If subject_index is not provided, returns the current subject's questions.
    """
    session_id = body.session_id
    subject_index = body.subject_index

    if subject_index is None:
        idx = get_current_subject_index(session_id)
        if idx is None:
            raise HTTPException(status_code=404, detail="Session not found")
        subject_index = idx

    result = get_current_questions(session_id, subject_index)
    if not result:
        raise HTTPException(status_code=404, detail="Subject not found in session")

    return {
        "success": True,
        "data": result,
    }


@router.post("/submit")
async def submit_challenge_answer(
    body: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Submit an answer for the current question.

    Returns immediate feedback (correct/incorrect, XP, explanation),
    and indicates whether the subject or entire session is complete.
    """
    if body.subject not in CORE_SUBJECTS:
        raise HTTPException(status_code=400, detail=f"Invalid subject. Must be one of: {', '.join(CORE_SUBJECTS)}")

    result = submit_answer(
        session_id=body.session_id,
        subject=body.subject,
        question_index=body.question_index,
        user_answer=body.user_answer,
        time_taken_seconds=body.time_taken_seconds,
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Session or question not found")

    return {
        "success": True,
        "result": result,
    }


class CompleteSessionRequest(BaseModel):
    session_id: str


@router.post("/complete")
async def complete_challenge_session(
    body: CompleteSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Complete a challenge session.

    Saves all responses to the database, updates user XP,
    and returns a detailed summary of performance.
    """
    summary = await complete_session(
        db=db,
        user_id=current_user.id,
        session_id=body.session_id,
    )

    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])

    return {
        "success": True,
        "summary": summary,
    }


@router.get("/summary")
async def get_summary(
    session_id: str = Query(..., description="The session ID"),
    current_user: User = Depends(get_current_user),
):
    """
    Get the current in-memory summary for a session (before finalisation).
    """
    summary = get_session_summary(session_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "success": True,
        "summary": summary,
    }
