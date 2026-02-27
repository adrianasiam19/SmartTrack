"""
auth/dependencies.py
────────────────────
FastAPI dependency that extracts and validates the current user from
the Authorization: Bearer <token> header on protected routes.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import decode_access_token, get_user_by_id
from app.database import get_db
from app.users.models import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency for protected routes:
      Authorization: Bearer <access_token>

    Usage:
        @router.get("/me")
        async def me(user: User = Depends(get_current_user)):
            ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    try:
        user_id = decode_access_token(credentials.credentials)
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(user_id, db)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )
    return user
