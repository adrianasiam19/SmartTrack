from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.recommendations.service import list_recommendations
from app.users.models import User

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/history")
async def recommendation_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return {"items": await list_recommendations(db, current_user.id)}
