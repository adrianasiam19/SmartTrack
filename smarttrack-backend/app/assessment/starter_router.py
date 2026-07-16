"""
starter_router.py — Starter Arena API endpoints for the adaptive onboarding experience
"""
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.users.models import User
from app.assessment.starter_arena import (
    generate_starter_session,
    generate_learner_profile,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/starter-arena", tags=["Starter Arena"])


class StartSessionRequest(BaseModel):
    psychometric_count: int = 5
    academic_count: int = 5


class QuestionModel(BaseModel):
    id: str
    type: str  # "psychometric" or "academic"
    question: str
    options: dict | list
    domain: Optional[str] = None
    category: Optional[str] = None
    display: Optional[str] = None
    correct_key: Optional[str] = None
    explanation: Optional[str] = None


class StartSessionResponse(BaseModel):
    session_id: str
    questions: list[QuestionModel]
    total_count: int


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str
    time_taken_seconds: float = 0


class CompleteSessionRequest(BaseModel):
    session_id: str
    psychometric_responses: list[dict] = []
    academic_responses: list[dict] = []


class LearnerProfileResponse(BaseModel):
    success: bool
    profile: Optional[dict] = None
    error: Optional[str] = None


@router.post("/start", response_model=StartSessionResponse)
async def start_session(
    body: StartSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start a new Starter Arena session.

    Generates a mixed session of psychometric and academic diagnostic questions
    adapted to the student's SHS level.
    """
    shs_level = current_user.shs_level or "SHS 1"
    programme = current_user.programme or "General Science"

    try:
        session = await generate_starter_session(
            db=db,
            user_id=str(current_user.id),
            shs_level=shs_level,
            programme=programme,
            psychometric_count=body.psychometric_count,
            academic_count=body.academic_count,
        )
        return StartSessionResponse(
            session_id=session["session_id"],
            questions=[QuestionModel(**q) for q in session["questions"]],
            total_count=session["total_count"],
        )
    except Exception as e:
        logger.error(f"Failed to start Starter Arena: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate session: {str(e)}",
        )


@router.post("/complete", response_model=LearnerProfileResponse)
async def complete_session(
    body: CompleteSessionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Complete the Starter Arena and generate a learner profile.

    Analyzes all responses to build a personalized learner profile
    including learning style, strengths, weaknesses, and recommendations.
    """
    shs_level = current_user.shs_level or "SHS 1"
    programme = current_user.programme or "General Science"

    if not body.psychometric_responses and not body.academic_responses:
        return LearnerProfileResponse(
            success=False,
            error="No responses provided for analysis.",
            profile=None,
        )

    try:
        profile = await generate_learner_profile(
            shs_level=shs_level,
            programme=programme,
            psychometric_responses=body.psychometric_responses,
            academic_responses=body.academic_responses,
        )
        return LearnerProfileResponse(success=True, profile=profile)
    except Exception as e:
        logger.error(f"Failed to generate learner profile: {e}")
        return LearnerProfileResponse(
            success=False,
            error=f"Failed to generate profile: {str(e)}",
        )
