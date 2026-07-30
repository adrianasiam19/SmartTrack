"""
KNUST Decision Tree recommendation adapter.

The Decision Tree is the PRIMARY programme recommendation engine.
Cut-off / rule lists are used as an explicit fallback when the model cannot run.
"""
from __future__ import annotations

import logging
import sys
import traceback
from pathlib import Path
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))


def _ml_enabled() -> bool:
    return bool(
        getattr(settings, "ML_RECOMMENDATIONS_ENABLED", True)
        and getattr(settings, "ML_ALTERNATE_ENABLED", True)
    )


def _ml_top_n() -> int:
    return int(
        getattr(settings, "ML_RECOMMENDATIONS_TOP_N", None)
        or getattr(settings, "ML_ALTERNATE_TOP_N", 8)
        or 8
    )


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
    Run the KNUST Decision Tree as the primary recommender.

    Still gated to Eligible∪Stretch bands from cut-offs when available so
    suggestions stay admission-realistic.
    """
    _ = xp, streak_days  # reserved for future DT features

    base: dict[str, Any] = {
        "enabled": False,
        "role": "primary",
        "model": "knust_dt",
        "model_loaded": False,
        "predictions": [],
        "programmes": [],
        "features_used": {},
        "disclaimer": "",
    }

    if not _ml_enabled():
        logger.info("Decision Tree recommendations disabled by settings")
        return {
            **base,
            "error": "ml_disabled",
            "error_detail": "ML_RECOMMENDATIONS_ENABLED is false",
        }

    try:
        from ml_aspect.knust_dt.predict import (
            grades_to_dt_features,
            load_model,
            model_status,
            predict_knust_dt_alternate,
        )
    except Exception as e:
        logger.exception("KNUST DT import failed — will fall back to cut-offs")
        return {
            **base,
            "error": "model_unavailable",
            "error_detail": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc()[-2500:],
            "model_status": {"exists": False, "cached": False},
        }

    status = model_status()
    try:
        load_model()
        status = model_status()
    except FileNotFoundError as e:
        logger.error("Decision Tree model file missing: %s", e)
        return {
            **base,
            "error": "model_file_missing",
            "error_detail": str(e),
            "model_status": status,
        }
    except Exception as e:
        logger.exception("Decision Tree model failed to load — falling back to cut-offs")
        return {
            **base,
            "error": "model_load_failed",
            "error_detail": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc()[-2500:],
            "model_status": {**status, "last_load_error": str(e)},
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
            top_n=_ml_top_n(),
        )
    except Exception as e:
        logger.exception("KNUST DT prediction failed — falling back to cut-offs")
        return {
            **base,
            "model_loaded": True,
            "error": "prediction_failed",
            "error_detail": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc()[-2500:],
            "model_status": status,
            "features_used": {},
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
        "role": "primary",
        "never_primary": False,
        "model": "knust_dt",
        "model_loaded": True,
        "title": "Programme matches",
        "gate": "eligible_or_stretch_only",
        "features_used": features,
        "features": {"aggregate": features.get("aggregate")},
        "predictions": predictions,
        "programmes": learner_programmes,
        "disclaimer": "",
        "training_note": "synthetic_mvp",
        "model_status": status,
        "error": None if learner_programmes else "empty_predictions",
        "error_detail": (
            None
            if learner_programmes
            else "Model ran but returned no Eligible/Stretch programmes for this profile."
        ),
    }


# Back-compat alias
generate_ml_knust_primary = generate_ml_knust_alternate
