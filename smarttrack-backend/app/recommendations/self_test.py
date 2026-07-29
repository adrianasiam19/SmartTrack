"""
End-to-end self-test for the KNUST Decision Tree recommendation pipeline.

Used by GET /api/v1/recommendations/self-test (development / debug only).
"""
from __future__ import annotations

import logging
import traceback
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = _BACKEND_ROOT / "ml_aspect" / "knust_dt" / "knust_dt_model.pkl"
DATASET_PATH = _BACKEND_ROOT / "ml_aspect" / "knust_dt" / "knust_dt_students.csv"
CUTOFFS_PATH = _BACKEND_ROOT / "data" / "knust_cutoffs_2025.json"

# Minimal synthetic WASSCE-like grades for a smoke prediction
_SMOKE_GRADES = [
    {"subject": "English Language", "grade": "B3"},
    {"subject": "Core Mathematics", "grade": "B2"},
    {"subject": "Integrated Science", "grade": "B3"},
    {"subject": "Social Studies", "grade": "C4"},
    {"subject": "Physics", "grade": "B3"},
    {"subject": "Chemistry", "grade": "B3"},
    {"subject": "Elective Mathematics", "grade": "B2"},
]


def _check(name: str, ok: bool, detail: str = "", **extra: Any) -> dict[str, Any]:
    item: dict[str, Any] = {"name": name, "ok": bool(ok), "detail": detail}
    item.update(extra)
    return item


def run_recommendation_self_test() -> dict[str, Any]:
    """
    Verify model artifact, dataset, feature build, prediction, and adapter output.
    Does not require a logged-in learner or database rows.
    """
    checks: list[dict[str, Any]] = []

    # 1) Model file
    model_exists = MODEL_PATH.exists()
    checks.append(
        _check(
            "decision_tree_model_exists",
            model_exists,
            str(MODEL_PATH),
            size_bytes=MODEL_PATH.stat().st_size if model_exists else 0,
        )
    )

    # 2) Synthetic dataset
    dataset_exists = DATASET_PATH.exists()
    checks.append(
        _check(
            "synthetic_dataset_exists",
            dataset_exists,
            str(DATASET_PATH),
            size_bytes=DATASET_PATH.stat().st_size if dataset_exists else 0,
        )
    )

    # 3) Cut-offs catalogue
    cutoffs_exist = CUTOFFS_PATH.exists()
    checks.append(
        _check(
            "knust_cutoffs_exist",
            cutoffs_exist,
            str(CUTOFFS_PATH),
        )
    )

    # 4) Model load
    model_loaded = False
    load_error = None
    n_classes = 0
    feature_columns: list[str] = []
    if model_exists:
        try:
            from ml_aspect.knust_dt.predict import load_model, MODEL_PATH as PREDICT_PATH

            bundle = load_model(PREDICT_PATH)
            model_loaded = bundle is not None and "model" in bundle
            classes = getattr(bundle.get("label_encoder"), "classes_", None)
            n_classes = len(classes) if classes is not None else 0
            feature_columns = list(bundle.get("feature_columns") or [])
            checks.append(
                _check(
                    "decision_tree_model_loads",
                    model_loaded,
                    f"classes={n_classes}",
                    feature_columns=feature_columns,
                )
            )
        except Exception as exc:
            load_error = f"{type(exc).__name__}: {exc}"
            logger.exception("Self-test: Decision Tree model failed to load")
            checks.append(
                _check(
                    "decision_tree_model_loads",
                    False,
                    load_error,
                    traceback=traceback.format_exc()[-2000:],
                )
            )
    else:
        checks.append(
            _check(
                "decision_tree_model_loads",
                False,
                "Skipped — model file missing",
            )
        )

    # 5) Feature vector
    features: dict[str, float] = {}
    if model_loaded:
        try:
            from ml_aspect.knust_dt.features import FEATURE_COLUMNS
            from ml_aspect.knust_dt.predict import grades_to_dt_features

            features = grades_to_dt_features(
                academic_grades=_SMOKE_GRADES,
                behavioral_traits={"analytical": 70, "empathy": 55, "practical": 60, "creative": 50},
                skill_estimates={"Math": 0.4, "Science": 0.3, "Logic": 0.2, "Verbal": 0.1},
            )
            missing = [c for c in FEATURE_COLUMNS if c not in features]
            checks.append(
                _check(
                    "feature_vector_generated",
                    len(missing) == 0 and bool(features),
                    f"keys={len(features)} missing={missing}",
                    features=features,
                )
            )
        except Exception as exc:
            logger.exception("Self-test: feature vector failed")
            checks.append(
                _check(
                    "feature_vector_generated",
                    False,
                    f"{type(exc).__name__}: {exc}",
                    traceback=traceback.format_exc()[-2000:],
                )
            )
    else:
        checks.append(
            _check("feature_vector_generated", False, "Skipped — model not loaded")
        )

    # 6) Prediction
    predictions: list[dict[str, Any]] = []
    if model_loaded and features:
        try:
            from app.recommendations.cutoffs import apply_cutoff_boundaries
            from ml_aspect.knust_dt.predict import predict_knust_dt_alternate

            knust_payload = apply_cutoff_boundaries(
                grades=_SMOKE_GRADES,
                family_fit_scores={
                    "Health Sciences": 60,
                    "Engineering": 70,
                    "Natural Sciences": 65,
                },
                limit_per_band=40,
            )
            predictions = predict_knust_dt_alternate(
                features,
                knust_payload=knust_payload,
                top_n=5,
            )
            checks.append(
                _check(
                    "prediction_runs",
                    len(predictions) > 0,
                    f"returned {len(predictions)} programmes",
                    top=[
                        {
                            "programme": p.get("programme"),
                            "confidence": p.get("confidence"),
                            "eligibility_band": p.get("eligibility_band"),
                        }
                        for p in predictions[:5]
                    ],
                )
            )
        except Exception as exc:
            logger.exception("Self-test: prediction failed")
            checks.append(
                _check(
                    "prediction_runs",
                    False,
                    f"{type(exc).__name__}: {exc}",
                    traceback=traceback.format_exc()[-2000:],
                )
            )
    else:
        checks.append(_check("prediction_runs", False, "Skipped — prerequisites failed"))

    # 7) Adapter / recommendation shape
    if model_loaded:
        try:
            from app.recommendations.ml_career import generate_ml_knust_alternate
            from app.recommendations.cutoffs import apply_cutoff_boundaries

            knust_payload = apply_cutoff_boundaries(
                grades=_SMOKE_GRADES,
                family_fit_scores={"Engineering": 70, "Natural Sciences": 65},
                limit_per_band=40,
            )
            ml = generate_ml_knust_alternate(
                academic_grades=_SMOKE_GRADES,
                behavioral_traits={"analytical": 70.0},
                skill_estimates={"Math": 0.4},
                knust_payload=knust_payload,
            )
            programmes = ml.get("programmes") or []
            ok = bool(ml.get("enabled")) and len(programmes) > 0
            checks.append(
                _check(
                    "recommendation_adapter_returns_results",
                    ok,
                    f"enabled={ml.get('enabled')} programmes={len(programmes)} error={ml.get('error')}",
                    model_loaded=ml.get("model_loaded"),
                    sample_programmes=[p.get("programme") for p in programmes[:5]],
                )
            )
        except Exception as exc:
            logger.exception("Self-test: recommendation adapter failed")
            checks.append(
                _check(
                    "recommendation_adapter_returns_results",
                    False,
                    f"{type(exc).__name__}: {exc}",
                    traceback=traceback.format_exc()[-2000:],
                )
            )
    else:
        checks.append(
            _check(
                "recommendation_adapter_returns_results",
                False,
                "Skipped — model not loaded",
            )
        )

    passed = sum(1 for c in checks if c["ok"])
    failed = [c["name"] for c in checks if not c["ok"]]
    return {
        "ok": len(failed) == 0,
        "passed": passed,
        "total": len(checks),
        "failed": failed,
        "checks": checks,
        "paths": {
            "model": str(MODEL_PATH),
            "dataset": str(DATASET_PATH),
            "cutoffs": str(CUTOFFS_PATH),
        },
    }
