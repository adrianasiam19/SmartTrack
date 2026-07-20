"""
train_model.py
──────────────
Trains the ATLAS career-recommendation model on the synthetic dataset and
evaluates it using TOP-3 accuracy — the metric that actually matters here,
since the product shows students a ranked top-3, not a single best guess.

Exports into model/:
  1. atlas_career_model.pkl   — joblib bundle (model + encoder + columns)
  2. model_schema.json         — plain-text feature/class list for sanity checks
  3. training_report.txt       — human-readable accuracy summary

Run: python train_model.py
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATA_PATH = Path(__file__).parent / "data" / "synthetic_students.csv"
MODEL_DIR = Path(__file__).parent / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


def top_k_accuracy(model, X, y_true_encoded, k=3) -> float:
    """Fraction of samples where the true label is among the top-k predicted
    probabilities. This is the metric that matches the actual product
    behaviour — ATLAS shows a ranked top-3, so a 'miss' only counts if the
    correct programme isn't in the top 3 at all."""
    proba = model.predict_proba(X)
    top_k_preds = np.argsort(proba, axis=1)[:, -k:]
    hits = [y_true_encoded[i] in top_k_preds[i] for i in range(len(y_true_encoded))]
    return float(np.mean(hits))


def main():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    # ── Feature columns: everything except the label and the track.
    # Track is dropped because it's almost a direct proxy for the label's
    # super-category — keeping it would make the problem artificially easy
    # and wouldn't reflect a real new user. ──
    target_col = "programme"
    drop_cols = [target_col, "track"]
    feature_cols = [c for c in df.columns if c not in drop_cols]

    X = df[feature_cols].copy()
    y_raw = df[target_col].copy()

    encoder = LabelEncoder()
    y = encoder.fit_transform(y_raw)

    print(f"Features ({len(feature_cols)}): {feature_cols}")
    print(f"Classes ({len(encoder.classes_)}): {list(encoder.classes_)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

    print("\nTraining RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=4,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    top1_acc = accuracy_score(y_test, y_pred)
    top3_acc = top_k_accuracy(model, X_test, y_test, k=3)

    report = classification_report(
        y_test, y_pred, target_names=encoder.classes_, zero_division=0
    )

    print(f"\nTop-1 accuracy: {top1_acc:.3f}")
    print(f"Top-3 accuracy: {top3_acc:.3f}")
    print(f"\n{report}")

    importances = pd.Series(model.feature_importances_, index=feature_cols)
    importances = importances.sort_values(ascending=False)
    print("Top 10 most important features:")
    print(importances.head(10))

    report_path = MODEL_DIR / "training_report.txt"
    with open(report_path, "w") as f:
        f.write("ATLAS Career Recommendation Model — Training Report\n")
        f.write("=" * 55 + "\n\n")
        f.write(f"Dataset: {DATA_PATH.name} ({len(df)} students)\n")
        f.write(f"Train/Test split: {len(X_train)} / {len(X_test)}\n\n")
        f.write(f"Top-1 accuracy: {top1_acc:.3f}\n")
        f.write(f"Top-3 accuracy: {top3_acc:.3f}\n\n")
        f.write("Per-class report:\n")
        f.write(report)
        f.write("\nTop 10 feature importances:\n")
        f.write(importances.head(10).to_string())
    print(f"\nSaved training report -> {report_path}")

    bundle = {
        "model": model,
        "label_encoder": encoder,
        "feature_columns": feature_cols,
    }
    bundle_path = MODEL_DIR / "atlas_career_model.pkl"
    joblib.dump(bundle, bundle_path)
    print(f"Saved model bundle -> {bundle_path}")

    schema_path = MODEL_DIR / "model_schema.json"
    with open(schema_path, "w") as f:
        json.dump({
            "feature_columns": feature_cols,
            "classes": list(encoder.classes_),
        }, f, indent=2)
    print(f"Saved model schema -> {schema_path}")


if __name__ == "__main__":
    main()
