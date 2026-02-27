"""
auth/router.py
──────────────
Authentication routes:

  POST  /auth/register        → Create new account (email + password)
  POST  /auth/login           → Login, receive access + refresh tokens
  POST  /auth/refresh         → Use refresh token to get new access token
  POST  /auth/logout          → Revoke refresh token
  GET   /auth/google/url      → Get Google OAuth consent screen URL
  POST  /auth/google/callback → Exchange Google code for tokens
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import schemas
from app.auth.service import (
    create_access_token,
    create_refresh_token,
    exchange_google_code,
    get_or_create_google_user,
    get_user_by_email,
    hash_password,
    revoke_refresh_token,
    validate_refresh_token,
    verify_password,
)
from app.config import settings
from app.database import get_db
from app.users.models import User
from app.users.schemas import UserPublic

router = APIRouter(prefix="/auth", tags=["Authentication"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


# ── Register ──────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=schemas.TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(body: schemas.RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new account with email and password."""
    existing = await get_user_by_email(body.email, db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()   # Get auto-generated user.id before creating tokens

    access_token = create_access_token(user.id)
    refresh_token = await create_refresh_token(user.id, db)

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=schemas.TokenResponse)
async def login(body: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    """Log in with email and password."""
    user = await get_user_by_email(body.email, db)

    # Don't reveal whether the email exists or the password is wrong
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
    )

    if not user or not user.password_hash:
        raise invalid
    if not verify_password(body.password, user.password_hash):
        raise invalid
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )

    user.last_login = datetime.now(timezone.utc)

    access_token = create_access_token(user.id)
    refresh_token = await create_refresh_token(user.id, db)

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# ── Refresh ───────────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=schemas.AccessTokenResponse)
async def refresh(body: schemas.RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    db_token = await validate_refresh_token(body.refresh_token, db)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or expired.",
        )
    access_token = create_access_token(db_token.user_id)
    return schemas.AccessTokenResponse(access_token=access_token)


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: schemas.RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Revoke the provided refresh token (invalidates this device's session)."""
    await revoke_refresh_token(body.refresh_token, db)


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.get("/google/url")
async def google_auth_url(redirect_uri: str):
    """
    Return the Google OAuth consent screen URL.
    The frontend opens this URL to start the OAuth flow.
    """
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return {"url": f"{GOOGLE_AUTH_URL}?{query}"}


@router.post("/google/callback", response_model=schemas.TokenResponse)
async def google_callback(
    body: schemas.GoogleCallbackRequest, db: AsyncSession = Depends(get_db)
):
    """
    Exchange the Google authorization code for our JWT tokens.
    The frontend sends the `code` and `redirect_uri` it used.
    """
    try:
        google_info = await exchange_google_code(body.code, body.redirect_uri)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Google.",
        )

    user = await get_or_create_google_user(google_info, db)

    access_token = create_access_token(user.id)
    refresh_token = await create_refresh_token(user.id, db)

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# ── Who am I ─────────────────────────────────────────────────────────────────
# (a quick self-check protected route — more routes live in users/router.py)

from app.auth.dependencies import get_current_user  # noqa: E402 — avoid circular

@router.get("/me", response_model=UserPublic)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's public profile."""
    return current_user
