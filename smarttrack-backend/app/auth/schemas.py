from pydantic import BaseModel, EmailStr, Field


# ── Registration ──────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)


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
