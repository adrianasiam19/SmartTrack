from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.recommendations.eligibility import evaluate_recommendation_eligibility
from app.recommendations.service import list_recommendations
from app.users.models import User

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/eligibility")
async def recommendation_eligibility(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Friendly unlock status for programme recommendations (phase levels mandatory)."""
    return await evaluate_recommendation_eligibility(db, current_user)


@router.get("/history")
async def recommendation_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"items": await list_recommendations(db, current_user.id)}
