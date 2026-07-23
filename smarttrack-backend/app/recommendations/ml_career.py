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
            "programmes": [],
            "disclaimer": "Learning profile insights are disabled.",
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
            "programmes": [],
            "error": "model_unavailable",
            "disclaimer": (
                "Learning profile insights are temporarily unavailable. "
                "Your main programme recommendations are unchanged."
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
            "programmes": [],
            "error": "model_file_missing",
            "disclaimer": (
                "Learning profile insights are temporarily unavailable. "
                "Your main programme recommendations are unchanged."
            ),
        }
    except Exception as e:
        logger.warning("KNUST DT alternate prediction failed: %s", e)
        return {
            "enabled": True,
            "role": "alternate",
            "model": "knust_dt",
            "predictions": [],
            "programmes": [],
            "error": "prediction_failed",
            "disclaimer": (
                "Learning profile insights could not be generated right now. "
                "Your main programme recommendations are unchanged."
            ),
        }

    from app.recommendations.presentation import format_ml_as_learner_programmes

    aggregate = None
    if knust_payload:
        aggregate = (knust_payload.get("aggregate") or {}).get("aggregate")
    learner_programmes = format_ml_as_learner_programmes(
        predictions, aggregate=aggregate
    )

    return {
        "enabled": True,
        "role": "alternate",
        "never_primary": True,
        "model": "knust_dt",
        "title": "Learning profile insights",
        "gate": "eligible_or_stretch_only",
        "features": {
            "aggregate": features.get("aggregate"),
        },
        "predictions": predictions,
        "programmes": learner_programmes,
        "disclaimer": (
            "Additional suggestions from Atlas' machine-learning model. "
            "This model was trained on synthetic (simulated) student profiles for the MVP, "
            "so results are exploratory and may be less accurate until real learner data is available."
        ),
        "training_note": "synthetic_mvp",
    }
