"""Post-phase psychometric checkpoint API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.phases.models import Phase
from app.psychometrics.models import PsychometricOption, PsychometricQuestion, UserPsychometricBankResponse
from app.psychometrics.selection import save_checkpoint_response, select_checkpoint_questions
from app.recommendations.service import generate_phase_recommendation
from app.users.models import User

router = APIRouter(prefix="/psychometrics", tags=["Psychometrics"])


class CheckpointQuestionOut(BaseModel):
    id: int
    bank_id: str
    number: int
    category: str
    text: str
    options: list[dict]


class CheckpointStartResponse(BaseModel):
    phase_id: int
    phase_number: int
    phase_label: str
    questions: list[CheckpointQuestionOut]


class CheckpointAnswerIn(BaseModel):
    question_id: int
    option_id: int


class CheckpointCompleteResponse(BaseModel):
    answered: int
    required: int
    complete: bool
    recommendation: dict | None = None


@router.post("/checkpoint/{phase_number}/start", response_model=CheckpointStartResponse)
async def start_checkpoint(
    phase_number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    phase = (
        await db.execute(select(Phase).where(Phase.number == phase_number))
    ).scalar_one_or_none()
    if not phase:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Phase not found")

    questions = await select_checkpoint_questions(db, current_user.id, phase.id)
    out = []
    for q in questions:
        out.append(
            CheckpointQuestionOut(
                id=q.id,
                bank_id=q.bank_id,
                number=q.number,
                category=q.category,
                text=q.text,
                options=[
                    {"id": o.id, "label": o.label, "text": o.text}
                    for o in sorted(q.options, key=lambda x: x.label)
                ],
            )
        )
    return CheckpointStartResponse(
        phase_id=phase.id,
        phase_number=phase.number,
        phase_label=phase.name,
        questions=out,
    )


@router.post("/checkpoint/{phase_number}/answer")
async def answer_checkpoint(
    phase_number: int,
    body: CheckpointAnswerIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    phase = (
        await db.execute(select(Phase).where(Phase.number == phase_number))
    ).scalar_one_or_none()
    if not phase:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Phase not found")

    opt = (
        await db.execute(
            select(PsychometricOption).where(PsychometricOption.id == body.option_id)
        )
    ).scalar_one_or_none()
    if not opt or opt.question_id != body.question_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid option")

    await save_checkpoint_response(
        db, current_user.id, phase.id, body.question_id, body.option_id
    )
    return {"ok": True}


@router.post("/checkpoint/{phase_number}/complete", response_model=CheckpointCompleteResponse)
async def complete_checkpoint(
    phase_number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.config import settings

    phase = (
        await db.execute(select(Phase).where(Phase.number == phase_number))
    ).scalar_one_or_none()
    if not phase:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Phase not found")

    answered = (
        await db.execute(
            select(func.count())
            .select_from(UserPsychometricBankResponse)
            .where(
                UserPsychometricBankResponse.user_id == current_user.id,
                UserPsychometricBankResponse.phase_id == phase.id,
            )
        )
    ).scalar_one()
    required = settings.PSYCHO_CHECKPOINT_COUNT
    if answered < required:
        return CheckpointCompleteResponse(
            answered=answered, required=required, complete=False, recommendation=None
        )

    rec = await generate_phase_recommendation(db, current_user.id, phase.id)
    return CheckpointCompleteResponse(
        answered=answered,
        required=required,
        complete=True,
        recommendation=rec,
    )
