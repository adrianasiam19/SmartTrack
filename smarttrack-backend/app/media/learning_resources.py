"""Extensible learning resource contracts for the Learning Center.

Videos are the first concrete kind. Future kinds (pdf, simulation, animation, link)
can plug into the same shape and the same /resources endpoint without redesigning
the lesson UI.
"""
from __future__ import annotations

from typing import Any, Literal

ResourceKind = Literal["video", "pdf", "simulation", "animation", "link"]


def learning_resource(
    *,
    id: str,
    kind: ResourceKind,
    title: str,
    url: str,
    provider: str,
    thumbnail_url: str | None = None,
    channel: str | None = None,
    duration_seconds: int | None = None,
    description: str | None = None,
    query: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": id,
        "kind": kind,
        "title": title,
        "url": url,
        "provider": provider,
        "thumbnail_url": thumbnail_url,
        "channel": channel,
        "duration_seconds": duration_seconds,
        "description": description,
        "query": query,
    }
    if extra:
        payload["extra"] = extra
    return payload
