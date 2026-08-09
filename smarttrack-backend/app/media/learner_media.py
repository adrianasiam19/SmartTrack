"""Stage 5 — Learner-facing media helpers.

Full attribution / source / license metadata is stored internally (cache, logs).
API payloads sent to the frontend expose only what the learner needs to see:
the image itself (and optional educational legend), never provider credits.
"""
from __future__ import annotations

from typing import Any

# Keys kept for internal compliance / debugging — never sent to learners.
INTERNAL_IMAGE_KEYS = frozenset(
    {
        "attribution",
        "source",
        "license",
        "query",
        "queries_used",
        "plan",
        "score",
        "score_factors",
        "cached_at",
        "size",
        "mime",
        "width",
        "height",
        "key",
    }
)


def extract_internal_attribution(image: dict[str, Any] | None) -> dict[str, Any] | None:
    """Keep compliance metadata separately from the learner payload."""
    if not isinstance(image, dict) or not image.get("url"):
        return None
    meta = {
        "attribution": image.get("attribution"),
        "source": image.get("source"),
        "license": image.get("license"),
        "query": image.get("query"),
        "concept": image.get("concept"),
        "url": image.get("url"),
    }
    return {k: v for k, v in meta.items() if v is not None}


def to_learner_image(image: dict[str, Any] | None) -> dict[str, Any] | None:
    """
    Public image payload for Learning Center / Challenges.

    Includes display fields only. Omits attribution, source, license, and
    retrieval diagnostics. The image URL is used as <img src> — it is not
    shown as visible text in the UI.
    """
    if not isinstance(image, dict):
        return None
    url = image.get("url")
    if not url:
        return None

    out: dict[str, Any] = {
        "url": url,
        "alt": image.get("alt") or image.get("concept") or "Educational diagram",
    }
    if image.get("concept"):
        out["concept"] = image.get("concept")
    if image.get("requires_labels") is not None:
        out["requires_labels"] = bool(image.get("requires_labels"))
    if image.get("labels"):
        out["labels"] = image.get("labels")
    if image.get("chart_data"):
        out["chart_data"] = image.get("chart_data")
    # Educational legend (what to look for) — not provider attribution
    if image.get("legend"):
        out["legend"] = image.get("legend")
    return out


def scrub_lesson_for_learner(lesson: dict[str, Any] | None) -> dict[str, Any]:
    """Strip internal visual metadata before API responses."""
    if not isinstance(lesson, dict):
        return {}
    out = dict(lesson)
    out.pop("visual_attribution_internal", None)
    out.pop("image_plan", None)
    out.pop("visual_need", None)
    visual = out.get("visual_aid")
    if isinstance(visual, dict):
        # Re-build a clean public visual (drops attribution if cached older lessons)
        cleaned = to_learner_image(visual)
        if cleaned and visual.get("legend") and "legend" not in cleaned:
            cleaned["legend"] = visual["legend"]
        out["visual_aid"] = cleaned
    return out


def scrub_image_dict(image: dict[str, Any] | None) -> dict[str, Any] | None:
    """Remove internal keys from an existing image dict (in place copy)."""
    return to_learner_image(image)
