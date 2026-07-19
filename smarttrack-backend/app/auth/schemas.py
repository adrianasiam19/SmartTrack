from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# Allowed SHS programmes & levels (Phase 1 — Science & Arts only).
Programme = Literal["General Science", "General Arts", "Business", "Visual Arts", "Home Economics", "Technical"]
SHSLevel = Literal["SHS 1", "SHS 2", "SHS 3", "Completed SHS"]


# ── Registration ──────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    programme: Programme
    shs_level: SHSLevel
    school: str | None = Field(default=None, max_length=255)


# ── Login ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Tokens ────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """Returned on successful login or registration."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    """Returned on a successful token refresh."""
    access_token: str
    token_type: str = "bearer"


# ── Google OAuth ──────────────────────────────────────────────────────────────

class GoogleCallbackRequest(BaseModel):
    """The `code` query param sent back from Google's OAuth consent screen."""
    code: str
    redirect_uri: str


# ── Password reset ────────────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    # Only returned in development when SMTP is not configured, for local testing.
    dev_reset_link: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=10)
    password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str
