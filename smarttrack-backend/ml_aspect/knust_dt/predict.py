"""
Serve-time KNUST Decision Tree alternate ranker.

Flow:
  1. Build features (aggregate + subject points + traits/accuracies)
  2. predict_proba over KNUST programme classes
  3. Keep ONLY programmes in Eligible ∪ Stretch from the primary cut-off payload
  4. Sort by model probability → alternate list

Never changes bands, aggregate, or XP. Never used as startup/primary.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd

from ml_aspect.knust_dt.features import FEATURE_COLUMNS, MISSING_SUBJECT_POINTS

MODEL_PATH = Path(__file__).resolve().parent / "knust_dt_model.pkl"
_model_cache = None


def load_model(model_path: Optional[Path] = None):
    global _model_cache
    if _model_cache is None:
        path = model_path or MODEL_PATH
        _model_cache = joblib.load(path)
    return _model_cache


def grades_to_dt_features(
    *,
    academic_grades: list[dict[str, str]],
    behavioral_traits: dict[str, float] | None = None,
    skill_estimates: dict[str, float] | None = None,
    grade_to_points_fn=None,
    compute_aggregate_fn=None,
) -> dict[str, float]:
    """Build DT feature dict from Atlas grades / traits / skills."""
    if grade_to_points_fn is None or compute_aggregate_fn is None:
        from app.recommendations.cutoffs import compute_wassce_aggregate, grade_to_points

        grade_to_points_fn = grade_to_points
        compute_aggregate_fn = compute_wassce_aggregate

    pts = {
        "english": MISSING_SUBJECT_POINTS,
        "core_maths": MISSING_SUBJECT_POINTS,
        "biology": MISSING_SUBJECT_POINTS,
        "chemistry": MISSING_SUBJECT_POINTS,
        "physics": MISSING_SUBJECT_POINTS,
        "elective_maths": MISSING_SUBJECT_POINTS,
        "integrated_science": MISSING_SUBJECT_POINTS,
        "social_studies": MISSING_SUBJECT_POINTS,
    }

    def _assign(subject: str, points: int) -> None:
        s = subject.lower()
        if "elective" in s and "math" in s:
            pts["elective_maths"] = min(pts["elective_maths"], float(points))
        elif "core math" in s or s in {"mathematics", "maths", "math"} or (
            "math" in s and "elective" not in s and "add" not in s
        ):
            pts["core_maths"] = min(pts["core_maths"], float(points))
        elif "english" in s:
            pts["english"] = min(pts["english"], float(points))
        elif "biology" in s:
            pts["biology"] = min(pts["biology"], float(points))
        elif "chemistry" in s:
            pts["chemistry"] = min(pts["chemistry"], float(points))
        elif "physics" in s:
            pts["physics"] = min(pts["physics"], float(points))
        elif "integrated science" in s or s == "science":
            pts["integrated_science"] = min(pts["integrated_science"], float(points))
        elif "social" in s:
            pts["social_studies"] = min(pts["social_studies"], float(points))

    for row in academic_grades or []:
        subject = str(row.get("subject") or "")
        grade = str(row.get("grade") or "")
        p = grade_to_points_fn(grade)
        if subject and p is not None:
            _assign(subject, p)

    agg_info = compute_aggregate_fn(academic_grades or [])
    aggregate = agg_info.get("aggregate")
    if aggregate is None:
        # Fallback sum of available cores + best others
        aggregate = int(
            pts["english"]
            + pts["core_maths"]
            + sum(
                sorted(
                    [
                        pts["biology"],
                        pts["chemistry"],
                        pts["physics"],
                        pts["elective_maths"],
                        pts["integrated_science"],
                        pts["social_studies"],
                    ]
                )[:4]
            )
        )

    traits_in = behavioral_traits or {}

    def trait(name: str, default: float = 50.0) -> float:
        for k, v in traits_in.items():
            if name in str(k).lower():
                val = float(v)
                return val * 100.0 if val <= 1.0 else val
        return default

    skills = skill_estimates or {}

    def theta_pct(domain: str, default: float = 50.0) -> float:
        if domain not in skills:
            return default
        return max(0.0, min(100.0, ((float(skills[domain]) + 3.0) / 6.0) * 100.0))

    return {
        "aggregate": float(aggregate),
        "pts_english": float(pts["english"]),
        "pts_core_maths": float(pts["core_maths"]),
        "pts_biology": float(pts["biology"]),
        "pts_chemistry": float(pts["chemistry"]),
        "pts_physics": float(pts["physics"]),
        "pts_elective_maths": float(pts["elective_maths"]),
        "pts_integrated_science": float(pts["integrated_science"]),
        "pts_social_studies": float(pts["social_studies"]),
        "trait_analytical": float(trait("analytical")),
        "trait_empathy": float(trait("empathy")),
        "trait_practical": float(trait("practical") or trait("persistence") or trait("carefulness")),
        "trait_creative": float(trait("creative")),
        "logic_accuracy": float(theta_pct("Logic")),
        "quant_accuracy": float(theta_pct("Math")),
        "scientific_accuracy": float(theta_pct("Science")),
        "verbal_accuracy": float(theta_pct("Verbal")),
    }


def predict_knust_dt_alternate(
    features: dict[str, float],
    *,
    knust_payload: dict[str, Any] | None,
    top_n: int = 5,
    model_path: Optional[Path] = None,
) -> list[dict[str, Any]]:
    """
    Rank KNUST programmes with the DT, restricted to Eligible ∪ Stretch.

    Reach is never returned here (stays informational on the primary cut-off UI).
    """
    bundle = load_model(model_path)
    model = bundle["model"]
    encoder = bundle["label_encoder"]
    columns = bundle.get("feature_columns") or FEATURE_COLUMNS

    row = {c: float(features.get(c, MISSING_SUBJECT_POINTS if c.startswith("pts_") else 50.0)) for c in columns}
    if "aggregate" in columns:
        row["aggregate"] = float(features.get("aggregate", 24))

    X = pd.DataFrame([row], columns=columns)
    proba = model.predict_proba(X)[0]
    class_names = list(encoder.classes_)

    allowed: dict[str, dict[str, Any]] = {}
    bands = (knust_payload or {}).get("bands") or {}
    for band_name in ("eligible", "stretch"):
        for item in bands.get(band_name) or []:
            name = str(item.get("programme") or "")
            if name:
                allowed[name] = {
                    "programme": name,
                    "family": item.get("family"),
                    "cutoff": item.get("cutoff"),
                    "demand": item.get("demand"),
                    "university": item.get("university", "KNUST"),
                    "cycle": item.get("cycle"),
                    "eligibility_band": band_name,
                    "aggregate": item.get("aggregate"),
                    "headroom": item.get("headroom"),
                }

    if not allowed:
        return []

    ranked: list[dict[str, Any]] = []
    for idx, name in enumerate(class_names):
        if name not in allowed:
            continue
        ranked.append(
            {
                **allowed[name],
                "confidence": float(proba[idx]),
                "source": "knust_dt_alternate",
                "role": "alternate",
                "model": "knust_dt",
            }
        )

    # Include eligible/stretch programmes the DT never saw as a class (rare) with 0 conf at end
    seen = {r["programme"] for r in ranked}
    for name, meta in allowed.items():
        if name not in seen:
            ranked.append(
                {
                    **meta,
                    "confidence": 0.0,
                    "source": "knust_dt_alternate",
                    "role": "alternate",
                    "model": "knust_dt",
                }
            )

    ranked.sort(
        key=lambda r: (
            0 if r.get("eligibility_band") == "eligible" else 1,
            -float(r["confidence"]),
        )
    )
    return ranked[: max(1, top_n)]
