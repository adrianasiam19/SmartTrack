"""
KNUST cut-off boundaries for Atlas recommendations (rule layer).

Cut-offs are hard eligibility constraints. Soft ranking (psych / challenges /
families) happens *inside* bands. Future ML should re-rank within bands only —
it must not invent eligibility or override cut-offs.

ML HOOK (not wired yet)
-----------------------
When a model arrives, call it from RecommendationEngine after
`apply_cutoff_boundaries(...)` with a feature dict like:
  {
    "aggregate": int | None,
    "aggregate_complete": bool,
    "family_fit_scores": {...},
    "psych_affinity": {...},          # from checkpoint tags
    "challenge_subject_accuracy": {...},
    "eligible_programmes": [...],     # already gated
    "stretch_programmes": [...],
  }
Return model scores only for programmes already in eligible/stretch lists,
then merge into the UI payload. Reach programmes stay informational.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# WASSCE grade → aggregate points (lower is better)
WASSCE_POINTS: dict[str, int] = {
    "A1": 1,
    "A": 1,
    "B2": 2,
    "B": 2,
    "B3": 3,
    "C4": 4,
    "C": 4,
    "C5": 5,
    "C6": 6,
    "D7": 7,
    "D": 7,
    "E8": 8,
    "E": 8,
    "F9": 9,
    "F": 9,
}

# Soft stretch buffer; Very High demand programmes get a tighter buffer.
STRETCH_BUFFER_DEFAULT = 2
STRETCH_BUFFER_BY_DEMAND = {
    "Very High": 1,
    "High": 2,
    "Medium": 2,
    "Low": 3,
}

FAMILY_ALIASES = {
    "Health Sciences": "Health Sciences",
    "Engineering": "Engineering",
    "Science": "Natural Sciences",
    "Natural Sciences": "Natural Sciences",
    "Computing & IT": "Natural Sciences",  # CS / Actuarial live under Science family cutoffs
}


@lru_cache(maxsize=1)
def load_knust_cutoffs() -> dict[str, Any]:
    path = Path(__file__).resolve().parent.parent.parent / "data" / "knust_cutoffs_2025.json"
    return json.loads(path.read_text(encoding="utf-8"))


def grade_to_points(grade: str) -> int | None:
    key = str(grade or "").strip().upper()
    return WASSCE_POINTS.get(key)


def _is_english(subject: str) -> bool:
    s = subject.lower()
    return "english" in s


def _is_core_maths(subject: str) -> bool:
    s = subject.lower()
    if "elective" in s and "math" in s:
        return False
    return "core math" in s or s in {"mathematics", "maths", "math"} or (
        "math" in s and "elective" not in s and "add" not in s
    )


def compute_wassce_aggregate(grades: list[dict[str, str]]) -> dict[str, Any]:
    """
    Approximate KNUST-style aggregate: Core English + Core Maths + best other
    subjects to make 6. Incomplete grade sets are flagged.
    """
    scored: list[tuple[str, str, int]] = []
    for row in grades or []:
        subject = str(row.get("subject") or "").strip()
        grade = str(row.get("grade") or "").strip()
        points = grade_to_points(grade)
        if not subject or points is None:
            continue
        scored.append((subject, grade.upper(), points))

    if not scored:
        return {
            "aggregate": None,
            "complete": False,
            "subjects_used": [],
            "grades_counted": 0,
            "missing": ["english", "core_maths", "electives"],
            "method": "best_six_with_core_english_maths",
        }

    english = [x for x in scored if _is_english(x[0])]
    maths = [x for x in scored if _is_core_maths(x[0])]
    others = [x for x in scored if not _is_english(x[0]) and not _is_core_maths(x[0])]

    chosen: list[tuple[str, str, int]] = []
    missing: list[str] = []

    if english:
        chosen.append(min(english, key=lambda x: x[2]))
    else:
        missing.append("english")

    if maths:
        chosen.append(min(maths, key=lambda x: x[2]))
    else:
        missing.append("core_maths")

    others_sorted = sorted(others, key=lambda x: x[2])
    need = max(0, 6 - len(chosen))
    chosen.extend(others_sorted[:need])

    if len(chosen) < 6:
        missing.append("electives")

    aggregate = sum(p for _, _, p in chosen) if chosen else None
    return {
        "aggregate": aggregate,
        "complete": len(chosen) >= 6 and not missing,
        "subjects_used": [
            {"subject": s, "grade": g, "points": p} for s, g, p in chosen
        ],
        "grades_counted": len(chosen),
        "missing": missing,
        "method": "best_six_with_core_english_maths",
    }


def eligibility_band(
    aggregate: int | None,
    cutoff: int,
    demand: str = "Medium",
) -> str:
    """
    eligible | stretch | reach | unknown
    unknown when aggregate cannot be computed.
    """
    if aggregate is None:
        return "unknown"
    buffer = STRETCH_BUFFER_BY_DEMAND.get(demand, STRETCH_BUFFER_DEFAULT)
    if aggregate <= cutoff:
        return "eligible"
    if aggregate <= cutoff + buffer:
        return "stretch"
    return "reach"


def apply_cutoff_boundaries(
    *,
    grades: list[dict[str, str]],
    family_fit_scores: dict[str, int] | None = None,
    limit_per_band: int = 8,
) -> dict[str, Any]:
    """
    Gate KNUST programmes by aggregate vs cut-off, then soft-rank using
    family fit scores (psych/challenge soft layer — not ML yet).
    """
    cutoffs = load_knust_cutoffs()
    aggregate_info = compute_wassce_aggregate(grades)
    aggregate = aggregate_info.get("aggregate")
    family_fit_scores = family_fit_scores or {}

    banded: dict[str, list[dict[str, Any]]] = {
        "eligible": [],
        "stretch": [],
        "reach": [],
        "unknown": [],
    }

    for row in cutoffs.get("programmes") or []:
        family = str(row.get("family") or "")
        programme = str(row.get("programme") or "")
        cutoff = int(row.get("cutoff") or 99)
        demand = str(row.get("demand") or "Medium")
        band = eligibility_band(aggregate, cutoff, demand)
        atlas_family = FAMILY_ALIASES.get(family, family)
        soft = int(family_fit_scores.get(atlas_family, family_fit_scores.get(family, 50)))
        headroom = None if aggregate is None else cutoff - int(aggregate)
        item = {
            "university": cutoffs.get("university", "KNUST"),
            "cycle": cutoffs.get("cycle"),
            "family": family,
            "programme": programme,
            "cutoff": cutoff,
            "demand": demand,
            "eligibility_band": band,
            "aggregate": aggregate,
            "headroom": headroom,
            "family_fit_score": soft,
            "level": row.get("level", "Degree"),
        }
        banded.setdefault(band, []).append(item)

    def _sort_key(item: dict[str, Any]) -> tuple:
        # Prefer higher soft fit, then lower (more competitive) cutoffs that still fit.
        return (-int(item.get("family_fit_score") or 0), int(item.get("cutoff") or 99))

    for key in banded:
        banded[key] = sorted(banded[key], key=_sort_key)[:limit_per_band]

    return {
        "university": cutoffs.get("university", "KNUST"),
        "cycle": cutoffs.get("cycle"),
        "aggregate": aggregate_info,
        "bands": banded,
        "counts": {k: len(v) for k, v in banded.items()},
        "ml_ready": False,
        "ml_note": (
            "Cut-off gating is rule-based. Future ML should re-rank programmes "
            "inside eligible/stretch only; it must not override eligibility_band."
        ),
    }
