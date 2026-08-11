"""
auth/service.py
───────────────
Core authentication business logic:
  • Password hashing/verification  (passlib/bcrypt)
  • JWT access token creation/verification  (python-jose)
  • Refresh token management  (stored hashed in DB)
  • Google OAuth user resolution  (authlib + httpx)
"""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client
import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.users.models import RefreshToken, User

# ── Password hashing ──────────────────────────────────────────────────────────

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def hash_password(plain: str) -> str:
    # bcrypt requires bytes
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    # bcrypt requires bytes for both plain and hashed
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── JWT Access Tokens ─────────────────────────────────────────────────────────

def create_access_token(user_id: uuid.UUID) -> str:
    """Create a short-lived JWT (default 15 min)."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> uuid.UUID:
    """Decode and verify a JWT. Raises JWTError on failure."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("type") != "access":
        raise JWTError("Invalid token type")
    return uuid.UUID(payload["sub"])


# ── Refresh Tokens ────────────────────────────────────────────────────────────

def _hash_token(raw: str) -> str:
    """SHA-256 hash the raw token before storing in DB."""
    return hashlib.sha256(raw.encode()).hexdigest()


async def create_refresh_token(user_id: uuid.UUID, db: AsyncSession) -> str:
    """Generate a secure random refresh token and store its hash in DB."""
    raw_token = secrets.token_urlsafe(64)
    hashed = _hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    db_token = RefreshToken(
        user_id=user_id,
        token=hashed,
        expires_at=expires_at,
    )
    db.add(db_token)
    await db.flush()        # Write to DB within current transaction
    return raw_token        # Return the raw token to send to client


async def validate_refresh_token(
    raw_token: str, db: AsyncSession
) -> RefreshToken | None:
    """Look up a refresh token by its hash and verify it's valid."""
    hashed = _hash_token(raw_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == hashed)
    )
    db_token = result.scalar_one_or_none()
    if db_token and db_token.is_valid:
        return db_token
    return None


async def revoke_refresh_token(raw_token: str, db: AsyncSession) -> None:
    """Revoke a specific refresh token (logout)."""
    hashed = _hash_token(raw_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == hashed)
    )
    db_token = result.scalar_one_or_none()
    if db_token:
        db_token.revoked = True


async def revoke_all_refresh_tokens(user_id: uuid.UUID, db: AsyncSession) -> None:
    """Revoke ALL refresh tokens for a user (e.g., on password change)."""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id, RefreshToken.revoked == False  # noqa: E712
        )
    )
    for token in result.scalars().all():
        token.revoked = True


# ── User Lookup Helpers ───────────────────────────────────────────────────────

async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    from sqlalchemy import func

    normalized = (email or "").strip().lower()
    if not normalized:
        return None
    result = await db.execute(
        select(User).where(func.lower(User.email) == normalized)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(user_id: uuid.UUID, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


# ── Google OAuth ──────────────────────────────────────────────────────────────

async def exchange_google_code(code: str, redirect_uri: str) -> dict:
    """Exchange the OAuth code for tokens and fetch user info from Google."""
    async with httpx.AsyncClient() as client:
        # 1. Exchange code → access token
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id_clean,
                "client_secret": (settings.GOOGLE_CLIENT_SECRET or "").strip(),
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_resp.raise_for_status()
        tokens = token_resp.json()

        # 2. Fetch user profile
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        userinfo_resp.raise_for_status()
        return userinfo_resp.json()


async def get_or_create_google_user(google_info: dict, db: AsyncSession) -> User:
    """
    Find existing user by google_id or email, or create a new one.
    Requires a Google-verified email address (not an unverified/alias-only identity).
    """
    if not google_info.get("email"):
        raise ValueError(
            "Google did not provide an email for this account. "
            "Use a Google account with a real, verified email address."
        )
    # Google sets email_verified when the address is confirmed.
    if google_info.get("email_verified") is False:
        raise ValueError(
            "That Google account email is not verified. "
            "Verify the email in your Google account settings, then try again."
        )

    google_id: str = google_info["sub"]
    email: str = str(google_info["email"]).strip().lower()
    name: str = google_info.get("name") or email.split("@")[0]
    avatar: str | None = google_info.get("picture")

    # Try by google_id first (most reliable)
    result = await db.execute(
        select(User).where(User.google_id == google_id)
    )
    user = result.scalar_one_or_none()

    if user:
        # Update avatar in case it changed
        previous_login = user.last_login
        try:
            from app.notifications.engine import notify_return_after_absence

            await notify_return_after_absence(db, user, previous_login=previous_login)
        except Exception:
            import logging

            logging.getLogger(__name__).exception(
                "Return-after-absence notification failed"
            )
        user.avatar_url = avatar
        user.last_login = datetime.now(timezone.utc)
        return user

    # Try by email (existing email/password account → do not auto-hijack)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        # Case-insensitive fallback for older mixed-case rows
        user = await get_user_by_email(email, db)

    if user:
        if user.password_hash and not user.google_id:
            # Prevent takeover: attacker registers victim email, then victim uses Google.
            raise ValueError(
                "An account with this email already exists. "
                "Sign in with your password, then you can link Google from your profile."
            )
        previous_login = user.last_login
        try:
            from app.notifications.engine import notify_return_after_absence

            await notify_return_after_absence(db, user, previous_login=previous_login)
        except Exception:
            import logging

            logging.getLogger(__name__).exception(
                "Return-after-absence notification failed"
            )
        user.google_id = google_id
        user.avatar_url = avatar or user.avatar_url
        user.is_verified = True
        user.last_login = datetime.now(timezone.utc)
        return user

    # Create brand-new user
    new_user = User(
        email=email.lower(),
        full_name=name,
        google_id=google_id,
        avatar_url=avatar,
        is_verified=True,       # Google emails are pre-verified
        password_hash=None,     # No password for OAuth users
        onboarding_completed=False,
        starter_arena_completed=False,
        xp=0,
        rank="Beginner",
        streak=0,
        last_login=datetime.now(timezone.utc),
    )
    db.add(new_user)
    await db.flush()
    return new_user


# ── Password reset ────────────────────────────────────────────────────────────

PASSWORD_RESET_TOKEN_HOURS = 1


def create_password_reset_token(
    user_id: uuid.UUID, email: str
) -> tuple[str, str, datetime]:
    """
    Short-lived JWT used only for password reset links.

    Returns (token, jti, expires_at). Persist `jti` in password_resets for
    single-use enforcement.
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=PASSWORD_RESET_TOKEN_HOURS)
    jti = secrets.token_urlsafe(16)
    payload = {
        "sub": str(user_id),
        "email": email.lower(),
        "exp": expire,
        "type": "password_reset",
        "jti": jti,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti, expire


def verify_password_reset_token(token: str) -> tuple[uuid.UUID, str, str]:
    """
    Validate a password-reset JWT.
    Returns (user_id, email, jti). Raises JWTError on failure.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("type") != "password_reset":
        raise JWTError("Invalid token type")
    user_id = uuid.UUID(payload["sub"])
    email = str(payload.get("email") or "")
    jti = str(payload.get("jti") or "").strip()
    if not email or not jti:
        raise JWTError("Missing email or jti claim")
    return user_id, email, jti


async def send_password_reset_email(email: str, reset_url: str) -> bool:
    """
    Send a password-reset email via Resend (`app.mailer.send_mail`).

    Returns True if Resend accepted the message. Raises on hard failures so
    callers can log; does not decide whether to expose a dev link.
    """
    import logging

    from app.mailer import send_mail

    log = logging.getLogger(__name__)
    subject = "Reset your Atlas password"
    text = (
        "Hi,\n\n"
        "We received a request to reset your Atlas password.\n\n"
        f"Open this link to choose a new password "
        f"(expires in {PASSWORD_RESET_TOKEN_HOURS} hour):\n"
        f"{reset_url}\n\n"
        "If you did not request this, you can ignore this email.\n\n"
        "— Atlas\n"
    )
    html = (
        "<p>Hi,</p>"
        "<p>We received a request to reset your Atlas password.</p>"
        f"<p><a href=\"{reset_url}\">Choose a new password</a> "
        f"(expires in {PASSWORD_RESET_TOKEN_HOURS} hour).</p>"
        f"<p style=\"word-break:break-all;color:#64748B;font-size:12px\">{reset_url}</p>"
        "<p>If you did not request this, you can ignore this email.</p>"
        "<p>— Atlas</p>"
    )
    await send_mail(to=email, subject=subject, html=html, text=text)
    log.info("Password reset email accepted by Resend for %s", email)
    return True