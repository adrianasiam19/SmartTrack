"""
Map ml_aspect career-model class labels → KNUST Science / Engineering / Health
programmes from data/knust_cutoffs_2025.json.

Classes with no KNUST catalogue row (Law, Accounting, Journalism, …) are
intentionally omitted so alternate ML output stays inside the KNUST system.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# ML class slug → one or more exact programme names in knust_cutoffs_2025.json
ML_CLASS_TO_KNUST_PROGRAMMES: dict[str, list[str]] = {
    "medicine-surgery": [
        "MBChB Medicine",
        "BSc Human Biology (Medicine)",
    ],
    "pharmacy": [
        "Doctor of Pharmacy",
    ],
    "nursing": [
        "BSc Nursing",
        "BSc Midwifery",
    ],
    "computer-science": [
        "BSc Computer Science",
        "BSc Computer Engineering",
    ],
    "electrical-engineering": [
        "BSc Electrical Engineering",
        "BSc Telecommunication Engineering",
        "BSc Biomedical Engineering",
    ],
    "engineering-civil": [
        "BSc Civil Engineering",
        "BSc Geological Engineering",
        "BSc Geomatic Engineering",
    ],
    "agriculture": [
        "BSc Agricultural Engineering",
        "BSc Agricultural Biotechnology",
        "BSc Environmental Science",
    ],
    # Remaining ML classes (law, accounting, …) have no Science/Eng/Health
    # cut-off rows in the current Atlas catalogue — excluded from KNUST output.
}

CUTOFFS_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "knust_cutoffs_2025.json"
)


@lru_cache(maxsize=1)
def load_knust_programme_index() -> dict[str, dict[str, Any]]:
    """programme name → catalogue row."""
    data = json.loads(CUTOFFS_PATH.read_text(encoding="utf-8"))
    index: dict[str, dict[str, Any]] = {}
    for row in data.get("programmes") or []:
        name = str(row.get("programme") or "")
        if name:
            index[name] = {
                "university": data.get("university", "KNUST"),
                "cycle": data.get("cycle"),
                "family": row.get("family"),
                "programme": name,
                "cutoff": row.get("cutoff"),
                "demand": row.get("demand"),
                "level": row.get("level", "Degree"),
            }
    return index


def knust_targets_for_ml_class(ml_class: str) -> list[dict[str, Any]]:
    """Resolve an ML class to KNUST catalogue rows (empty if out of scope)."""
    index = load_knust_programme_index()
    out: list[dict[str, Any]] = []
    for name in ML_CLASS_TO_KNUST_PROGRAMMES.get(ml_class, []):
        row = index.get(name)
        if row:
            out.append(dict(row))
    return out


def all_mapped_ml_classes() -> list[str]:
    return sorted(ML_CLASS_TO_KNUST_PROGRAMMES.keys())
