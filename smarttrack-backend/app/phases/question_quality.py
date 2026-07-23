"""Post-generation quality gates for challenge items."""
from __future__ import annotations

import re
from typing import Any

from app.media.educational_images import mentions_visual

INCOMPLETE_FILL_RE = re.compile(
    r"(?i)\b("
    r"amount spent|from the (table|chart|graph|figure|diagram)|"
    r"shown (above|below|in the)|using the (data|table|chart)|"
    r"activity shown|in the figure|read (from|the) (graph|chart)"
    r")\b"
)


def fill_blank_is_self_contained(payload: dict[str, Any]) -> bool:
    """Fill-blank must include enough given data in stem+template (not rely on missing visuals)."""
    opts = payload.get("options") if isinstance(payload.get("options"), dict) else {}
    template = str(opts.get("template") or "")
    stem = str(payload.get("question_text") or "")
    combined = f"{stem}\n{template}".strip()
    if len(combined) < 40:
        return False
    # Must contain either digits (numeric problem) or substantial prose context
    has_digit = bool(re.search(r"\d", combined))
    has_choices_context = "___" in template and len(re.sub(r"_+", "", template)) > 25
    if INCOMPLETE_FILL_RE.search(combined) and not mentions_visual(combined):
        # Refers to missing table/chart without providing numbers
        if not has_digit:
            return False
    if INCOMPLETE_FILL_RE.search(combined) and "shown" in combined.lower() and not payload.get("image"):
        return False
    return has_digit or has_choices_context


def visual_without_image(payload: dict[str, Any]) -> bool:
    text = str(payload.get("question_text") or "")
    opts = payload.get("options") if isinstance(payload.get("options"), dict) else {}
    template = str(opts.get("template") or "")
    combined = f"{text} {template}"
    has_image = bool(payload.get("image") or (isinstance(opts, dict) and opts.get("image")))
    return mentions_visual(combined) and not has_image


def needs_labelled_diagram(payload: dict[str, Any]) -> bool:
    text = str(payload.get("question_text") or "")
    qtype = str(payload.get("question_type") or "")
    if qtype == "diagram_label":
        return True
    return bool(
        re.search(
            r"(?i)\b(labelled|labeled|label\s+[A-D]|part\s+[A-D]|which\s+label|arrow\s+points)\b",
            text,
        )
    )
