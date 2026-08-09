"""Load and query course_directory.json (lru_cache, same pattern as cutoffs)."""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "course_directory.json"

BRIEF_KEYS = (
    "slug",
    "name",
    "field",
    "level",
    "typical_duration",
    "brief",
    "related_shs_subjects",
    "commonly_offered_at",
)


@lru_cache(maxsize=1)
def load_course_directory() -> dict[str, Any]:
    if not _DATA_PATH.exists():
        logger.warning("Course directory JSON missing at %s", _DATA_PATH)
        return {"note": "", "fields": [], "programmes": []}
    try:
        raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("Failed to parse course directory JSON at %s", _DATA_PATH)
        return {"note": "", "fields": [], "programmes": []}
    if not isinstance(raw, dict):
        logger.warning("Course directory JSON root is not an object")
        return {"note": "", "fields": [], "programmes": []}
    programmes = raw.get("programmes") or []
    if not isinstance(programmes, list):
        programmes = []
    fields = raw.get("fields") or []
    if not isinstance(fields, list):
        fields = []
    cleaned = [p for p in programmes if isinstance(p, dict) and p.get("slug")]
    if not cleaned:
        logger.warning("Course directory loaded with zero programmes from %s", _DATA_PATH)
    return {
        "note": str(raw.get("note") or ""),
        "fields": [str(f) for f in fields],
        "programmes": cleaned,
    }


def list_fields() -> list[str]:
    data = load_course_directory()
    fields = list(data.get("fields") or [])
    if fields:
        return fields
    # Fallback: derive from programmes
    seen: list[str] = []
    for p in data.get("programmes") or []:
        field = str(p.get("field") or "").strip()
        if field and field not in seen:
            seen.append(field)
    return seen


def _as_brief(row: dict[str, Any]) -> dict[str, Any]:
    return {k: row.get(k) for k in BRIEF_KEYS}


def list_programmes(*, field: str | None = None, q: str | None = None) -> list[dict[str, Any]]:
    data = load_course_directory()
    rows = list(data.get("programmes") or [])
    field_key = (field or "").strip().lower()
    query = (q or "").strip().lower()

    out: list[dict[str, Any]] = []
    for row in rows:
        if field_key and str(row.get("field") or "").strip().lower() != field_key:
            continue
        if query:
            hay = " ".join(
                [
                    str(row.get("name") or ""),
                    str(row.get("brief") or ""),
                    str(row.get("field") or ""),
                    " ".join(str(x) for x in (row.get("core_topics") or [])),
                    " ".join(str(x) for x in (row.get("career_paths") or [])),
                ]
            ).lower()
            if query not in hay:
                continue
        out.append(_as_brief(row))
    out.sort(key=lambda r: (str(r.get("field") or ""), str(r.get("name") or "")))
    return out


def get_programme(slug: str) -> dict[str, Any] | None:
    key = (slug or "").strip().lower()
    if not key:
        return None
    for row in load_course_directory().get("programmes") or []:
        if str(row.get("slug") or "").strip().lower() == key:
            return dict(row)
    return None
