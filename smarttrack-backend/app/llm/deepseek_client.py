"""Shared DeepSeek client with fail-fast timeouts and a circuit breaker.

When DNS / network to api.deepseek.com fails, challenge generation used to wait
25–35s per LLM call × analysis × planner × question × retries — hanging Start.

This module:
  • uses a short connect timeout so DNS failures fail in seconds
  • opens a circuit after repeated transport errors
  • lets callers skip LLM and use bank / rule fallbacks immediately
"""
from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

DEEPSEEK_CHAT_URL = "https://api.deepseek.com/v1/chat/completions"

# After this many consecutive transport failures, skip LLM for COOLDOWN seconds.
_FAILURE_THRESHOLD = 2
_COOLDOWN_SECONDS = 120.0

_consecutive_failures = 0
_circuit_open_until = 0.0


def llm_circuit_open() -> bool:
    """True while DeepSeek should be skipped (recent connectivity failures)."""
    return time.monotonic() < _circuit_open_until


def llm_circuit_remaining_seconds() -> float:
    return max(0.0, _circuit_open_until - time.monotonic())


def _record_success() -> None:
    global _consecutive_failures, _circuit_open_until
    _consecutive_failures = 0
    _circuit_open_until = 0.0


def _record_transport_failure(exc: BaseException) -> None:
    global _consecutive_failures, _circuit_open_until
    _consecutive_failures += 1
    logger.warning(
        "DeepSeek transport failure (%s/%s): %s",
        _consecutive_failures,
        _FAILURE_THRESHOLD,
        exc,
    )
    if _consecutive_failures >= _FAILURE_THRESHOLD:
        _circuit_open_until = time.monotonic() + _COOLDOWN_SECONDS
        logger.error(
            "DeepSeek circuit OPEN for %.0fs — using bank/rule fallbacks",
            _COOLDOWN_SECONDS,
        )


def _is_transport_error(exc: BaseException) -> bool:
    if isinstance(
        exc,
        (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.WriteTimeout,
            httpx.PoolTimeout,
            httpx.NetworkError,
            httpx.TimeoutException,
        ),
    ):
        return True
    # Windows DNS: [Errno 11001] getaddrinfo failed
    text = str(exc).lower()
    return any(
        token in text
        for token in (
            "getaddrinfo",
            "name or service not known",
            "nodename nor servname",
            "all connection attempts failed",
            "temporarily unavailable",
            "network is unreachable",
        )
    )


def deepseek_timeout(*, read: float | None = None) -> httpx.Timeout:
    """Fail DNS/connect quickly; allow a longer read for successful responses."""
    read_s = float(
        read
        if read is not None
        else getattr(settings, "CHALLENGE_LLM_TIMEOUT_SECONDS", 20.0)
    )
    connect_s = float(getattr(settings, "CHALLENGE_LLM_CONNECT_TIMEOUT_SECONDS", 3.0))
    return httpx.Timeout(read_s, connect=connect_s)


async def deepseek_chat_completion(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    read_timeout: float | None = None,
    purpose: str = "chat",
) -> dict[str, Any] | None:
    """
    POST /chat/completions. Returns the parsed response JSON body, or None.

    Skips the network call entirely when the circuit is open.
    """
    if not (getattr(settings, "DEEPSEEK_API_KEY", "") or "").strip():
        return None
    if llm_circuit_open():
        logger.info(
            "DeepSeek skipped (%s) — circuit open %.0fs remaining",
            purpose,
            llm_circuit_remaining_seconds(),
        )
        return None

    payload: dict[str, Any] = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    try:
        async with httpx.AsyncClient(timeout=deepseek_timeout(read=read_timeout)) as client:
            res = await client.post(
                DEEPSEEK_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if res.status_code != 200:
            logger.warning(
                "DeepSeek %s HTTP %s: %s",
                purpose,
                res.status_code,
                (res.text or "")[:180],
            )
            return None
        _record_success()
        return res.json()
    except Exception as exc:
        if _is_transport_error(exc):
            _record_transport_failure(exc)
        else:
            logger.warning("DeepSeek %s failed: %s", purpose, exc)
        return None


async def deepseek_message_content(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    read_timeout: float | None = None,
    purpose: str = "chat",
) -> str | None:
    """Convenience: return assistant message content string, or None."""
    body = await deepseek_chat_completion(
        messages,
        temperature=temperature,
        max_tokens=max_tokens,
        read_timeout=read_timeout,
        purpose=purpose,
    )
    if not body:
        return None
    try:
        return str(body["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError):
        return None
