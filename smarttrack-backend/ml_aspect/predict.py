"""
predict.py
──────────
Inference for ATLAS career model — KNUST-aligned alternate recommendations.

PRIMARY product path is always cut-off gating in app/recommendations/cutoffs.py.
This module is ALTERNATE ONLY: profile-fit suggestions mapped onto the KNUST
Science / Engineering / Health catalogue. Never use as startup / primary list.

    from predict import predict_knust_alternates

    results = predict_knust_alternates(student_input, top_n=5)
    # -> KNUST programme rows with confidence (not raw ML slugs)

REQUIREMENTS:
    pip install scikit-learn joblib pandas numpy
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd

try:
    from ml_aspect.knust_mapping import knust_targets_for_ml_class
except ImportError:  # running as a script inside ml_aspect/
    from knust_mapping import knust_targets_for_ml_class

MODEL_PATH = Path(__file__).parent / "atlas_career_model.pkl"

FEATURE_DEFAULTS = {
    "wassce_biology": 5,
    "wassce_business_management": 5,
    "wassce_chemistry": 5,
    "wassce_core_maths": 5,
    "wassce_economics": 5,
    "wassce_elective_maths": 5,
    "wassce_english": 5,
    "wassce_financial_accounting": 5,
    "wassce_government": 5,
    "wassce_history": 5,
    "wassce_integrated_science": 5,
    "wassce_literature": 5,
    "wassce_physics": 5,
    "wassce_social_studies": 5,
    "trait_analytical": 50,
    "trait_creative": 50,
    "trait_social": 50,
    "trait_practical": 50,
    "trait_leadership": 50,
    "trait_empathy": 50,
    "logic_accuracy": 50,
    "quant_accuracy": 50,
    "verbal_accuracy": 50,
    "scientific_accuracy": 50,
    "xp": 0,
    "streak_days": 0,
}

_model_cache = None


def load_model(model_path: Optional[Path] = None):
    """Load the model bundle once and cache it."""
    global _model_cache
    if _model_cache is None:
        path = model_path or MODEL_PATH
        _model_cache = joblib.load(path)
    return _model_cache


def _build_feature_row(student_input: dict, feature_columns: list) -> pd.DataFrame:
    row = {}
    for col in feature_columns:
        if col in student_input:
            row[col] = student_input[col]
        elif col in FEATURE_DEFAULTS:
            row[col] = FEATURE_DEFAULTS[col]
        else:
            raise ValueError(
                f"Missing required feature '{col}' with no default available. "
                f"Check model_schema.json for the full required feature list."
            )
    return pd.DataFrame([row], columns=feature_columns)


def predict_top_programmes(
    student_input: dict,
    top_n: int = 3,
    model_path: Optional[Path] = None,
) -> list[dict]:
    """
    Raw model classes (legacy). Prefer predict_knust_alternates for Atlas.
    """
    bundle = load_model(model_path)
    model = bundle["model"]
    encoder = bundle["label_encoder"]
    feature_columns = bundle["feature_columns"]

    X = _build_feature_row(student_input, feature_columns)
    proba = model.predict_proba(X)[0]

    top_indices = np.argsort(proba)[::-1][:top_n]
    programme_names = encoder.inverse_transform(top_indices)

    return [
        {"programme": str(programme_names[i]), "confidence": float(proba[idx])}
        for i, idx in enumerate(top_indices)
    ]


def predict_knust_alternates(
    student_input: dict,
    top_n: int = 5,
    model_path: Optional[Path] = None,
    eligibility_by_programme: Optional[dict[str, str]] = None,
) -> list[dict[str, Any]]:
    """
    Alternate KNUST recommendations from the career model.

    - Maps ML class probabilities onto programmes in the KNUST cut-off catalogue.
    - Drops ML classes with no Science/Engineering/Health mapping.
    - Does NOT compute or change aggregates / eligibility bands.
    - Optional eligibility_by_programme annotates each row with the band from
      the primary cut-off engine (informational only).

    Returns list of:
      {
        "programme": "BSc Nursing",
        "family": "Health Sciences",
        "cutoff": 9,
        "demand": "High",
        "university": "KNUST",
        "cycle": "2025/2026",
        "confidence": 0.22,
        "ml_class": "nursing",
        "eligibility_band": "stretch" | null,
        "source": "ml_alternate",
        "role": "alternate",
      }
    """
    bundle = load_model(model_path)
    model = bundle["model"]
    encoder = bundle["label_encoder"]
    feature_columns = bundle["feature_columns"]

    X = _build_feature_row(student_input, feature_columns)
    proba = model.predict_proba(X)[0]
    class_names = list(encoder.classes_)

    # Best confidence per KNUST programme name
    best: dict[str, dict[str, Any]] = {}
    for idx, ml_class in enumerate(class_names):
        conf = float(proba[idx])
        if conf <= 0:
            continue
        for target in knust_targets_for_ml_class(str(ml_class)):
            name = target["programme"]
            row = {
                **target,
                "confidence": conf,
                "ml_class": str(ml_class),
                "eligibility_band": (eligibility_by_programme or {}).get(name),
                "source": "ml_alternate",
                "role": "alternate",
            }
            prev = best.get(name)
            if prev is None or conf > float(prev["confidence"]):
                best[name] = row

    ranked = sorted(best.values(), key=lambda r: float(r["confidence"]), reverse=True)
    return ranked[: max(1, top_n)]


if __name__ == "__main__":
    sample_student = {
        "wassce_biology": 2,
        "wassce_chemistry": 2,
        "wassce_physics": 3,
        "wassce_core_maths": 2,
        "wassce_english": 3,
        "trait_analytical": 80,
        "trait_empathy": 85,
        "trait_practical": 70,
        "logic_accuracy": 75,
        "quant_accuracy": 70,
        "verbal_accuracy": 65,
        "scientific_accuracy": 80,
        "xp": 900,
        "streak_days": 14,
    }
    print("Raw ML classes:")
    for r in predict_top_programmes(sample_student, top_n=3):
        print(f"  {r['programme']:<25} confidence={r['confidence']:.3f}")
    print("\nKNUST alternate programmes:")
    for r in predict_knust_alternates(sample_student, top_n=5):
        print(
            f"  {r['programme']:<45} family={r['family']:<16} "
            f"cut≤{r['cutoff']} conf={r['confidence']:.3f}"
        )
