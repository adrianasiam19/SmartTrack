"""
starter_router.py — Starter Arena API endpoints for the adaptive onboarding experience
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.users.models import User
from app.assessment.models import PsychometricResponse, StarterArenaResponse
from app.assessment.starter_arena import (
    generate_starter_session,
    generate_learner_profile,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/starter-arena", tags=["Starter Arena"])


class StartSessionRequest(BaseModel):
    psychometric_count: int = Field(default=6, ge=4, le=8)
    academic_count: int = Field(default=6, ge=4, le=8)


class QuestionModel(BaseModel):
    id: str
    type: str  # psychometric | cognitive
    question: str
    options: dict | list = {}
    domain: Optional[str] = None
    category: Optional[str] = None
    cognitive_skill: Optional[str] = None
    format: Optional[str] = None
    source: Optional[str] = None
    display: Optional[str] = None
    correct_key: Optional[str] = None
    explanation: Optional[str] = None


class StartSessionResponse(BaseModel):
    session_id: str
    questions: list[QuestionModel]
    total_count: int


class CompleteSessionRequest(BaseModel):
    session_id: str
    psychometric_responses: list[dict] = []
    academic_responses: list[dict] = []
    cognitive_responses: list[dict] = []


class LearnerProfileResponse(BaseModel):
    success: bool
    profile: Optional[dict] = None
    error: Optional[str] = None


def _persist_responses(
    *,
    current_user: User,
    session_id: str,
    responses: list[dict],
    default_type: str,
) -> list[StarterArenaResponse]:
    rows: list[StarterArenaResponse] = []
    for response in responses:
        question_id = str(response.get("question_id") or response.get("id") or "").strip()
        question_text = str(response.get("question") or "").strip()
        answer = str(response.get("answer") or "").strip()
        if not question_id or not question_text or not answer:
            continue
        question_type = str(response.get("type") or default_type)
        source = str(
            response.get("source")
            or ("database" if question_type == "psychometric" else "llm")
        )
        rows.append(
            StarterArenaResponse(
                user_id=current_user.id,
                session_id=session_id,
                question_id=question_id,
                question_text=question_text,
                question_type=question_type,
                source=source,
                category=response.get("category") or response.get("domain"),
                cognitive_skill=response.get("cognitive_skill"),
                question_format=str(
                    response.get("format")
                    or response.get("question_format")
                    or ("choose" if question_type == "psychometric" else "multiple-choice")
                ),
                options=response.get("options") or {},
                answer=answer,
                correct=response.get("correct"),
                time_taken_seconds=float(response.get("time_taken") or 0),
            )
        )
    return rows


@router.post("/start", response_model=StartSessionResponse)
async def start_session(
    body: StartSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start a new Starter Arena session.

    Returns a balanced alternating stream of unique psychometric database cards
    and LLM-generated cognitive discovery questions.
    """
    if current_user.starter_arena_completed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Starter Arena has already been completed for this account.",
        )

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
            questions=[QuestionModel(**question) for question in session["questions"]],
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
    db: AsyncSession = Depends(get_db),
):
    """
    Complete the Starter Arena, store every response, and generate a learner profile.
    """
    shs_level = current_user.shs_level or "SHS 1"
    programme = current_user.programme or "General Science"
    cognitive_responses = body.cognitive_responses or body.academic_responses

    if not body.psychometric_responses and not cognitive_responses:
        return LearnerProfileResponse(
            success=False,
            error="No responses provided for analysis.",
            profile=None,
        )

    try:
        # Keep the legacy psychometric table for challenge-arena uniqueness checks.
        for response in body.psychometric_responses:
            question_id = str(response.get("question_id", ""))
            answer = str(response.get("answer", ""))
            card_id = (
                question_id.replace("psych_", "")
                if question_id.startswith("psych_")
                else question_id
            )
            if not card_id or not answer:
                continue
            db.add(
                PsychometricResponse(
                    user_id=current_user.id,
                    card_id=card_id[:50],
                    answer=answer[:10],
                )
            )

        for row in _persist_responses(
            current_user=current_user,
            session_id=body.session_id,
            responses=body.psychometric_responses,
            default_type="psychometric",
        ):
            db.add(row)
        for row in _persist_responses(
            current_user=current_user,
            session_id=body.session_id,
            responses=cognitive_responses,
            default_type="cognitive",
        ):
            db.add(row)

        profile = await generate_learner_profile(
            shs_level=shs_level,
            programme=programme,
            psychometric_responses=body.psychometric_responses,
            academic_responses=cognitive_responses,
        )

        current_user.starter_arena_completed = True
        current_user.onboarding_completed = True
        current_user.learner_profile = profile
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)

        return LearnerProfileResponse(success=True, profile=profile)
    except Exception as e:
        logger.error(f"Failed to generate learner profile: {e}")
        await db.rollback()
        return LearnerProfileResponse(
            success=False,
            error=f"Failed to generate profile: {str(e)}",
        )
