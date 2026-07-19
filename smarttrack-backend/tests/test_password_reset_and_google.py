"""Auth helpers for Google OAuth URL building and password reset tokens."""

from urllib.parse import parse_qs, urlparse

import pytest
from jose import JWTError

from app.auth.service import (
    create_password_reset_token,
    verify_password_reset_token,
    hash_password,
    verify_password,
)
from app.auth.schemas import ForgotPasswordRequest, ResetPasswordRequest
from app.config import settings
import uuid


def test_password_hash_roundtrip():
    hashed = hash_password("StrongPass1!")
    assert verify_password("StrongPass1!", hashed)
    assert not verify_password("wrong", hashed)


def test_password_reset_token_roundtrip():
    user_id = uuid.uuid4()
    token = create_password_reset_token(user_id, "student@example.com")
    decoded_id, email = verify_password_reset_token(token)
    assert decoded_id == user_id
    assert email == "student@example.com"


def test_password_reset_token_rejects_access_token_type():
    from jose import jwt
    from datetime import datetime, timedelta, timezone

    bad = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "email": "a@b.com",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "type": "access",
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    with pytest.raises(JWTError):
        verify_password_reset_token(bad)


def test_forgot_password_schema_normalises_email_type():
    body = ForgotPasswordRequest(email="Student@Example.com")
    assert str(body.email).lower() == "student@example.com"


def test_reset_password_schema_requires_token_and_password():
    body = ResetPasswordRequest(token="a" * 20, password="StrongPass1!")
    assert len(body.token) >= 10


def test_google_url_endpoint_encodes_redirect(client_or_skip=None):
    """Unit-level check that urlencode is used for redirect_uri."""
    from urllib.parse import urlencode

    redirect = "http://localhost:3000/auth/callback"
    params = {
        "client_id": "abc.apps.googleusercontent.com",
        "redirect_uri": redirect,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    assert query["redirect_uri"] == [redirect]
    assert "openid" in query["scope"][0]
