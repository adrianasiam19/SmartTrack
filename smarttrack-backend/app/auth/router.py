"""
auth/router.py
──────────────
Authentication routes:

  POST  /auth/register         → Create new account (email + password)
  POST  /auth/login            → Login, receive access + refresh tokens
  POST  /auth/refresh          → Use refresh token to get new access token
  POST  /auth/logout           → Revoke refresh token
  GET   /auth/google/url       → Get Google OAuth consent screen URL
  POST  /auth/google/callback  → Exchange Google code for tokens
  POST  /auth/forgot-password  → Email a password reset link
  POST  /auth/reset-password   → Set a new password from a reset token
"""
from urllib.parse import urlencode
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import schemas
from app.auth.models import PasswordReset
from app.auth.service import (
    create_access_token,
    create_refresh_token,
    exchange_google_code,
    get_or_create_google_user,
    get_user_by_email,
    hash_password,
    revoke_refresh_token,
    revoke_all_refresh_tokens,
    validate_refresh_token,
    verify_password,
    create_password_reset_token,
    verify_password_reset_token,
    send_password_reset_email,
)
from app.auth.validators import validate_password_strength, PasswordValidationError
from app.config import settings
from app.database import get_db
from app.users.models import User
from app.users.schemas import UserPublic

logger = logging.getLogger(__name__)

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
    # Validate password strength
    try:
        validate_password_strength(body.password)
    except PasswordValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
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
        programme=body.programme,
        shs_level=body.shs_level,
        school=body.school,
        onboarding_completed=False,
        starter_arena_completed=False,
        # Initialize gamification stats
        xp=0,
        rank="Beginner",
        streak=0,
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

    previous_login = user.last_login
    try:
        from app.notifications.engine import notify_return_after_absence

        await notify_return_after_absence(db, user, previous_login=previous_login)
    except Exception:
        import logging

        logging.getLogger(__name__).exception("Return-after-absence notification failed")

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
    await db.commit()  # Commit the revocation to database


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.get("/google/url")
async def google_auth_url(redirect_uri: str):
    """
    Return the Google OAuth consent screen URL.
    The frontend opens this URL to start the OAuth flow.
    """
    if not settings.google_oauth_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Sign-In is not configured on this server.",
        )

    params = {
        "client_id": settings.google_client_id_clean,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    return {"url": f"{GOOGLE_AUTH_URL}?{urlencode(params)}"}


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
    except Exception as exc:
        logger.warning("Google code exchange failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Google.",
        )

    user = await get_or_create_google_user(google_info, db)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )

    access_token = create_access_token(user.id)
    refresh_token = await create_refresh_token(user.id, db)

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# ── Forgot / reset password ───────────────────────────────────────────────────

async def _send_reset_email_safe(email: str, reset_url: str) -> None:
    """Background send — never raises into the HTTP response."""
    try:
        await send_password_reset_email(email, reset_url)
    except Exception:
        logger.exception("Password reset email failed for %s", email)


@router.post("/forgot-password", response_model=schemas.ForgotPasswordResponse)
async def forgot_password(
    body: schemas.ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset email.

    Always returns a generic success message so account existence is not leaked.
    Google-only accounts cannot reset a password they do not have.

    Dev fallback: `dev_reset_link` is returned only when ENVIRONMENT is not
    production (independent of whether Resend credentials are present).
    """
    generic = (
        "Password reset instructions have been sent to your email address."
    )
    user = await get_user_by_email(body.email.lower(), db)
    dev_reset_link: str | None = None
    is_production = (settings.ENVIRONMENT or "").strip().lower() == "production"

    if user and user.password_hash and user.is_active:
        token, jti, expires_at = create_password_reset_token(user.id, user.email)
        # Invalidate any previous unused tokens for this user (single active reset).
        await db.execute(
            update(PasswordReset)
            .where(
                PasswordReset.user_id == user.id,
                PasswordReset.used_at.is_(None),
            )
            .values(used_at=datetime.now(timezone.utc))
        )
        db.add(
            PasswordReset(
                jti=jti,
                user_id=user.id,
                expires_at=expires_at,
            )
        )
        # Persist ledger before email so a crash mid-send cannot orphan a usable token
        # without a DB row (and so background send always races after commit).
        await db.commit()

        reset_url = (
            f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={token}"
        )
        background_tasks.add_task(_send_reset_email_safe, user.email, reset_url)

        # Safe local aid: expose link in non-production only (not gated on API keys).
        if not is_production:
            dev_reset_link = reset_url
            logger.info("Dev password reset link for %s: %s", user.email, reset_url)

    return schemas.ForgotPasswordResponse(message=generic, dev_reset_link=dev_reset_link)


@router.post("/reset-password", response_model=schemas.MessageResponse)
async def reset_password(
    body: schemas.ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """Set a new password using a valid, unused reset token from the email link."""
    from jose import JWTError

    try:
        validate_password_strength(body.password)
    except PasswordValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    try:
        user_id, email, jti = verify_password_reset_token(body.token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset link is invalid or has expired.",
        )

    now = datetime.now(timezone.utc)
    reset_row = (
        await db.execute(select(PasswordReset).where(PasswordReset.jti == jti))
    ).scalar_one_or_none()
    if (
        reset_row is None
        or reset_row.used_at is not None
        or reset_row.expires_at <= now
        or reset_row.user_id != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset link is invalid or has expired.",
        )

    user = await db.get(User, user_id)
    if not user or not user.is_active or user.email.lower() != email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset link is invalid or has expired.",
        )
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses Google Sign-In. Please continue with Google instead.",
        )

    user.password_hash = hash_password(body.password)
    reset_row.used_at = now
    await revoke_all_refresh_tokens(user.id, db)

    return schemas.MessageResponse(
        message="Your password has been updated. You can now sign in."
    )


# ── Who am I ─────────────────────────────────────────────────────────────────
# (a quick self-check protected route — more routes live in users/router.py)

from app.auth.dependencies import get_current_user  # noqa: E402 — avoid circular

@router.get("/me", response_model=UserPublic)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's public profile."""
    return current_user
