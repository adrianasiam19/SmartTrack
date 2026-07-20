"""
Train DecisionTreeClassifier on rule-labeled KNUST data.

Run (from smarttrack-backend):
  python -m ml_aspect.knust_dt.generate_data
  python -m ml_aspect.knust_dt.train
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, top_k_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml_aspect.knust_dt.features import FEATURE_COLUMNS

DATA_PATH = Path(__file__).resolve().parent / "knust_dt_students.csv"
MODEL_PATH = Path(__file__).resolve().parent / "knust_dt_model.pkl"
SCHEMA_PATH = Path(__file__).resolve().parent / "knust_dt_schema.json"
REPORT_PATH = Path(__file__).resolve().parent / "knust_dt_report.txt"


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(f"Missing {DATA_PATH}. Run generate_data first.")

    df = pd.read_csv(DATA_PATH)
    # Drop ultra-rare labels so stratify works
    counts = df["label_programme"].value_counts()
    keep = counts[counts >= 5].index
    df = df[df["label_programme"].isin(keep)].copy()

    X = df[FEATURE_COLUMNS]
    y_raw = df["label_programme"].astype(str)

    encoder = LabelEncoder()
    y = encoder.fit_transform(y_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = DecisionTreeClassifier(
        max_depth=14,
        min_samples_leaf=8,
        min_samples_split=16,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    top1 = accuracy_score(y_test, y_pred)
    proba = model.predict_proba(X_test)
    # top_k_accuracy_score needs labels covering all classes
    top3 = top_k_accuracy_score(y_test, proba, k=min(3, len(encoder.classes_)), labels=range(len(encoder.classes_)))

    report = (
        "KNUST Decision Tree Ranker — Training Report\n"
        "============================================\n\n"
        "Labels: rule-based (cut-offs Eligible/Stretch + deterministic soft score).\n"
        "No LLM involved.\n\n"
        f"Rows: {len(df)}  Train: {len(X_train)}  Test: {len(X_test)}\n"
        f"Classes (programmes): {len(encoder.classes_)}\n"
        f"Top-1 accuracy: {top1:.3f}\n"
        f"Top-3 accuracy: {top3:.3f}\n"
        f"Features: {FEATURE_COLUMNS}\n"
    )
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)

    bundle = {
        "model": model,
        "label_encoder": encoder,
        "feature_columns": FEATURE_COLUMNS,
        "role": "alternate",
        "gate": "eligible_or_stretch_only",
        "teacher": "cutoffs_plus_deterministic_soft_score",
    }
    joblib.dump(bundle, MODEL_PATH)
    SCHEMA_PATH.write_text(
        json.dumps(
            {
                "feature_columns": FEATURE_COLUMNS,
                "classes": list(encoder.classes_),
                "role": "alternate",
                "gate": "eligible_or_stretch_only",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Saved model -> {MODEL_PATH}")
    print(f"Saved schema -> {SCHEMA_PATH}")


if __name__ == "__main__":
    main()
