"""Structured, learner-friendly recommendation error / notice helpers."""
from __future__ import annotations

from typing import Any


def recommendation_error(
    *,
    code: str,
    title: str,
    message: str,
    short_message: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "title": title,
        "message": message,
        "short_message": short_message or message,
    }
    if extra:
        payload.update(extra)
    return payload


PHASE_INCOMPLETE = recommendation_error(
    code="phase_not_completed",
    title="Phase not yet completed",
    message=(
        "You have not finished all levels in a challenge phase yet.\n\n"
        "Complete every level in at least one phase, then return here to unlock "
        "your programme recommendations."
    ),
    short_message="Complete all levels in this phase before requesting recommendations.",
)

NO_ACADEMIC_UPLOAD = recommendation_error(
    code="wassce_upload_missing",
    title="WASSCE results not uploaded yet",
    message=(
        "You already have programme matches from your Atlas activity.\n\n"
        "Upload WASSCE or academic results only when you want Atlas to refine those "
        "matches with your aggregate and admission cut-offs. This step is optional."
    ),
    short_message="WASSCE upload is optional — use it to refine admission insights.",
)

GRADES_NOT_EXTRACTED = recommendation_error(
    code="wassce_extraction_failed",
    title="WASSCE results could not be extracted",
    message=(
        "We could not read subject grades from your upload.\n\n"
        "Please re-upload a clearer WASSCE results PDF or image (good lighting, full page visible) "
        "so Atlas can calculate your aggregate and recommend suitable programmes."
    ),
    short_message="WASSCE results could not be extracted. Please re-upload a clearer file.",
)

AGGREGATE_UNAVAILABLE = recommendation_error(
    code="aggregate_unavailable",
    title="Aggregate could not be computed",
    message=(
        "Your grades were found, but Atlas could not compute a reliable WASSCE aggregate yet.\n\n"
        "Check that English, Core Mathematics, and enough elective subjects appear with valid "
        "grades (A1–F9), then try Get Recommendations again."
    ),
    short_message="Aggregate could not be computed from the grades we found.",
)

NO_MATCHING_PROGRAMMES = recommendation_error(
    code="no_matching_programmes",
    title="No matching programmes yet",
    message=(
        "Atlas could not find programmes that fit your current aggregate and profile.\n\n"
        "This can happen if grades are incomplete or the aggregate is outside the usual range. "
        "Re-check your uploaded results, or continue building your challenge profile and try again."
    ),
    short_message="No matching programmes were found for your current results.",
)

ML_FALLBACK_NOTICE = (
    "Your recommendations are based on admission cut-offs for now. "
    "Our advanced matching model was temporarily unavailable — developers have been notified."
)
