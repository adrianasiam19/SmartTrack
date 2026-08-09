"""
Central email sender (Resend).

The rest of the app should call `send_mail(...)` only — never talk to Resend
or SMTP directly from routers.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


async def send_mail(
    *,
    to: str,
    subject: str,
    html: str,
    text: str | None = None,
) -> dict[str, Any]:
    """
    Send one email via Resend.

    Raises RuntimeError if RESEND_API_KEY / MAIL_FROM are missing, or if Resend
    returns a non-success status. Callers that must not fail the HTTP response
    should catch and log.
    """
    api_key = (settings.RESEND_API_KEY or "").strip()
    mail_from = (settings.MAIL_FROM or "").strip()
    if not api_key:
        raise RuntimeError("RESEND_API_KEY is not configured")
    if not mail_from:
        raise RuntimeError("MAIL_FROM is not configured")

    payload: dict[str, Any] = {
        "from": mail_from,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if text:
        payload["text"] = text

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if response.status_code >= 400:
        logger.error(
            "Resend send failed status=%s body=%s",
            response.status_code,
            response.text[:500],
        )
        raise RuntimeError(f"Resend send failed ({response.status_code})")

    try:
        return response.json()
    except Exception:
        return {"ok": True}


def assert_mailer_ready_for_environment() -> None:
    """Fail loudly at startup in production if email is not configured."""
    if (settings.ENVIRONMENT or "").strip().lower() != "production":
        return
    if not (settings.RESEND_API_KEY or "").strip():
        raise RuntimeError(
            "RESEND_API_KEY is required when ENVIRONMENT=production "
            "(password-reset email must not silently degrade)."
        )
    if not (settings.MAIL_FROM or "").strip():
        raise RuntimeError(
            "MAIL_FROM is required when ENVIRONMENT=production."
        )
