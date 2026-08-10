"""Lightweight schema checks for scraped programme JSON."""
from __future__ import annotations

from typing import Any

REQUIRED_ROOT = ("university", "university_code", "scraped_at", "status", "programmes")
REQUIRED_PROGRAMME = ("id", "name", "university", "university_code", "source_url", "level")


def validate_university_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be an object"]
    for key in REQUIRED_ROOT:
        if key not in payload:
            errors.append(f"missing root field: {key}")
    programmes = payload.get("programmes")
    if programmes is None:
        return errors + ["programmes missing"]
    if not isinstance(programmes, list):
        return errors + ["programmes must be a list"]
    for i, row in enumerate(programmes):
        if not isinstance(row, dict):
            errors.append(f"programmes[{i}] must be an object")
            continue
        for key in REQUIRED_PROGRAMME:
            if not str(row.get(key) or "").strip():
                errors.append(f"programmes[{i}] missing {key}")
    return errors
