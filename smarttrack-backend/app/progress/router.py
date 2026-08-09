"""Authenticated Personal Progress API."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.progress.schemas import PersonalProgressResponse
from app.progress.service import build_personal_progress
from app.users.models import User

router = APIRouter(prefix="/progress", tags=["Personal Progress"])


@router.get("/me", response_model=PersonalProgressResponse)
async def get_my_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Personal Progress for the signed-in learner (Stages 1–2).

    Includes core stats, weekly summary, visualizations, Next Goal,
    motivational insights, and a typed future_modules extension slot
    (leaderboard disabled by default). No peer rankings in MVP.
    """
    return await build_personal_progress(db, current_user)
