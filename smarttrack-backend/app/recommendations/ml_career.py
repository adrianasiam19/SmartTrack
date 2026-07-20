"""
Build features and run the KNUST Decision Tree alternate ranker.

Primary recommendations always come from cutoffs.py + RecommendationEngine.
This module is ALTERNATE ONLY (Eligible/Stretch re-rank). Never startup/primary.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


def generate_ml_knust_alternate(
    *,
    academic_grades: list[dict[str, str]],
    behavioral_traits: dict[str, float] | None = None,
    skill_estimates: dict[str, float] | None = None,
    xp: int = 0,
    streak_days: int = 0,
    knust_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    DT alternate: reorder Eligible∪Stretch by learned soft preference.
    Does not invent programmes outside the primary cut-off bands.
    """
    _ = xp, streak_days  # reserved for future DT features; not used in v1 schema

    if not settings.ML_ALTERNATE_ENABLED:
        return {
            "enabled": False,
            "role": "alternate",
            "model": "knust_dt",
            "predictions": [],
            "disclaimer": "ML alternate recommendations are disabled.",
        }

    try:
        from ml_aspect.knust_dt.predict import (
            grades_to_dt_features,
            predict_knust_dt_alternate,
        )
    except Exception as e:
        logger.warning("KNUST DT alternate unavailable (import failed): %s", e)
        return {
            "enabled": False,
            "role": "alternate",
            "model": "knust_dt",
            "predictions": [],
            "error": "model_unavailable",
            "disclaimer": (
                "ML alternate could not load. Primary KNUST cut-off matches are unchanged."
            ),
        }

    try:
        features = grades_to_dt_features(
            academic_grades=academic_grades,
            behavioral_traits=behavioral_traits,
            skill_estimates=skill_estimates,
        )
        predictions = predict_knust_dt_alternate(
            features,
            knust_payload=knust_payload,
            top_n=settings.ML_ALTERNATE_TOP_N,
        )
    except FileNotFoundError:
        return {
            "enabled": False,
            "role": "alternate",
            "model": "knust_dt",
            "predictions": [],
            "error": "model_file_missing",
            "disclaimer": (
                "Train the KNUST DT first (python -m ml_aspect.knust_dt.generate_data && "
                "python -m ml_aspect.knust_dt.train). Primary cut-offs unchanged."
            ),
        }
    except Exception as e:
        logger.warning("KNUST DT alternate prediction failed: %s", e)
        return {
            "enabled": True,
            "role": "alternate",
            "model": "knust_dt",
            "predictions": [],
            "error": "prediction_failed",
            "disclaimer": (
                "ML alternate failed to run. Primary KNUST cut-off matches are unchanged."
            ),
        }

    return {
        "enabled": True,
        "role": "alternate",
        "never_primary": True,
        "model": "knust_dt",
        "gate": "eligible_or_stretch_only",
        "university": "KNUST",
        "cycle": (knust_payload or {}).get("cycle") or "2025/2026",
        "features": {
            "aggregate": features.get("aggregate"),
            "pts_english": features.get("pts_english"),
            "pts_core_maths": features.get("pts_core_maths"),
        },
        "predictions": predictions,
        "disclaimer": (
            "Alternate Decision Tree ranking inside your Eligible/Stretch KNUST "
            "programmes only (rule-labeled teacher, no LLM). "
            "Primary admissions list is still the cut-off bands above."
        ),
    }
