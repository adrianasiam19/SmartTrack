from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.recommendations.eligibility import evaluate_recommendation_eligibility
from app.recommendations.self_test import run_recommendation_self_test
from app.recommendations.service import list_recommendations
from app.users.models import User

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def _debug_allowed() -> bool:
    return bool(
        getattr(settings, "RECOMMENDATION_DEBUG", False)
        or str(getattr(settings, "ENVIRONMENT", "")).lower() == "development"
    )


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


@router.get("/self-test")
async def recommendation_self_test(
    current_user: User = Depends(get_current_user),
):
    """
    End-to-end Decision Tree + recommendation pipeline probe.

    Available in development, or when RECOMMENDATION_DEBUG=true.
    Requires a logged-in user (any account) — not shown in the learner UI.
    """
    _ = current_user
    if not _debug_allowed():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation self-test is only available in development/debug mode.",
        )
    return run_recommendation_self_test()
