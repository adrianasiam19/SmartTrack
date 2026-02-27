"""
users/router.py
───────────────
User profile routes (all protected):

  GET   /users/me         → Get own profile
  PATCH /users/me         → Update own profile
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.users.models import User
from app.users.schemas import UserPublic, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublic)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's full profile."""
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_profile(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the authenticated user's profile (name and/or avatar)."""
    updated = False
    if body.full_name is not None:
        current_user.full_name = body.full_name
        updated = True
    if body.avatar_url is not None:
        current_user.avatar_url = body.avatar_url
        updated = True

    if updated:
        db.add(current_user)

    return current_user
