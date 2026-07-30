"""
Compatibility facade for educational images.

New code should use:
  - app.media.image_plan.ImagePlanner
  - app.media.image_retrieval.ImageRetrievalService

This module keeps mentions_visual / resolve_educational_image for older callers.
"""
from __future__ import annotations

import re
from typing import Any

from app.media.image_plan import ImagePlan, ImagePlanner
from app.media.image_retrieval import retrieve_for_plan

DIAGRAM_LANGUAGE_RE = re.compile(
    r"\b("
    r"diagram|figure|illustration|"
    r"shown\s+(below|above|here|in\s+the|on\s+the)|"
    r"activity\s+shown|image\s+shown|picture\s+shown|"
    r"study\s+the\s+(image|picture|map|graph|diagram|figure)|"
    r"look\s+at\s+the\s+(image|picture|map|graph|diagram|figure)|"
    r"the\s+(image|picture|map|graph|diagram|figure)\s+(shows|below|above)|"
    r"labelled|label\s+the|from\s+the\s+chart|in\s+the\s+graph"
    r")\b",
    re.I,
)


def mentions_visual(text: str) -> bool:
    return bool(DIAGRAM_LANGUAGE_RE.search(text or ""))


async def resolve_educational_image(
    query: str,
    *,
    preferred_alt: str | None = None,
    requires_labels: bool = False,
    subject: str = "",
) -> dict[str, Any] | None:
    """Legacy helper — builds a minimal ImagePlan and retrieves."""
    plan = ImagePlan(
        needed=True,
        concept=preferred_alt or query,
        subject=subject,
        image_type="labelled_diagram" if requires_labels else "scientific_diagram",
        requires_labels=requires_labels,
        preferred_format="svg" if requires_labels else "png",
        search_keywords=[query] if query else [],
    )
    return await retrieve_for_plan(plan)


def extract_image_query_from_text(question_text: str, subject: str = "") -> str | None:
    plan = ImagePlanner.plan_from_lesson(
        title=(question_text or "")[:100],
        subject=subject,
        introduction=question_text or "",
    )
    return plan.primary_query() or None


def subject_image_hint(subject: str, question_text: str) -> str | None:
    return extract_image_query_from_text(question_text, subject)
