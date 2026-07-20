"""
Generate synthetic students labeled by KNUST cut-offs + deterministic soft score.

No LLM. Run:
  python -m ml_aspect.knust_dt.generate_data
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml_aspect.knust_dt.features import FEATURE_COLUMNS, MISSING_SUBJECT_POINTS
from ml_aspect.knust_dt.soft_label import programme_soft_score

CUTOFFS_PATH = ROOT / "data" / "knust_cutoffs_2025.json"
OUT_CSV = Path(__file__).resolve().parent / "knust_dt_students.csv"
N_STUDENTS = 5000
RNG = np.random.default_rng(42)

GRADE_LETTERS = ["A1", "B2", "B3", "C4", "C5", "C6", "D7", "E8", "F9"]
POINTS = {g: i + 1 for i, g in enumerate(GRADE_LETTERS)}  # A1=1 … F9=9


def _load_programmes() -> list[dict]:
    data = json.loads(CUTOFFS_PATH.read_text(encoding="utf-8"))
    return list(data.get("programmes") or [])


def _eligibility(aggregate: int, cutoff: int, demand: str) -> str:
    buffer = {"Very High": 1, "High": 2, "Medium": 2, "Low": 3}.get(demand, 2)
    if aggregate <= cutoff:
        return "eligible"
    if aggregate <= cutoff + buffer:
        return "stretch"
    return "reach"


def _sample_points(rng: np.random.Generator, mean: float, sd: float = 1.4) -> float:
    return float(np.clip(np.round(rng.normal(mean, sd)), 1, 9))


def _aggregate_from_points(pts: dict[str, float]) -> int:
    """Best-six style: english + core maths + best 4 others among available."""
    eng = pts["english"]
    maths = pts["core_maths"]
    others = [
        pts["biology"],
        pts["chemistry"],
        pts["physics"],
        pts["elective_maths"],
        pts["integrated_science"],
        pts["social_studies"],
    ]
    others_sorted = sorted(others)[:4]
    return int(round(eng + maths + sum(others_sorted)))


def generate_row(rng: np.random.Generator, programmes: list[dict]) -> dict | None:
    # Ability band so strong students unlock competitive programmes (Medicine, Eng, …)
    ability = rng.choice(["strong", "mid", "weak"], p=[0.35, 0.40, 0.25])
    ability_shift = {"strong": -1.8, "mid": 0.0, "weak": 1.6}[ability]

    archetype = rng.choice(
        ["health", "engineering", "science", "mixed"], p=[0.28, 0.28, 0.28, 0.16]
    )
    means = {
        "english": 3.5,
        "core_maths": 3.5,
        "biology": 5.0,
        "chemistry": 5.0,
        "physics": 5.0,
        "elective_maths": 5.0,
        "integrated_science": 4.0,
        "social_studies": 4.0,
    }
    if archetype == "health":
        means.update({"biology": 2.2, "chemistry": 2.5, "physics": 4.0, "core_maths": 3.5})
    elif archetype == "engineering":
        means.update({"elective_maths": 2.0, "physics": 2.2, "core_maths": 2.0, "chemistry": 3.5})
    elif archetype == "science":
        means.update({"elective_maths": 2.5, "physics": 3.0, "chemistry": 3.0, "biology": 3.5})

    pts = {k: _sample_points(rng, m + ability_shift) for k, m in means.items()}
    for key in ("biology", "chemistry", "physics", "elective_maths"):
        if rng.random() < 0.05:
            pts[key] = MISSING_SUBJECT_POINTS

    aggregate = _aggregate_from_points(pts)

    traits = {
        "analytical": float(np.clip(rng.normal(55 if archetype != "engineering" else 75, 15), 10, 95)),
        "empathy": float(np.clip(rng.normal(70 if archetype == "health" else 45, 15), 10, 95)),
        "practical": float(np.clip(rng.normal(70 if archetype == "engineering" else 50, 15), 10, 95)),
        "creative": float(np.clip(rng.normal(50, 15), 10, 95)),
    }
    accuracies = {
        "logic": float(np.clip(rng.normal(60, 15), 20, 95)),
        "quant": float(np.clip(rng.normal(65 if archetype != "health" else 55, 15), 20, 95)),
        "scientific": float(np.clip(rng.normal(70 if archetype != "engineering" else 55, 15), 20, 95)),
        "verbal": float(np.clip(rng.normal(55, 15), 20, 95)),
    }

    eligible: list[dict] = []
    stretch: list[dict] = []
    for row in programmes:
        band = _eligibility(aggregate, int(row["cutoff"]), str(row.get("demand") or "Medium"))
        if band == "eligible":
            eligible.append(row)
        elif band == "stretch":
            stretch.append(row)

    pool = eligible or stretch
    if not pool:
        return None

    scored = [
        (
            programme_soft_score(
                row,
                aggregate=aggregate,
                pts=pts,
                traits=traits,
                accuracies=accuracies,
            ),
            row["programme"],
        )
        for row in pool
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    # Weighted pick among top-5 to keep label diversity while staying near teacher optimum
    top = scored[: min(5, len(scored))]
    logits = np.array([s for s, _ in top], dtype=float)
    logits = logits - logits.max()
    weights = np.exp(logits / 8.0)
    weights = weights / weights.sum()
    label = str(rng.choice([p for _, p in top], p=weights))

    return {
        "aggregate": float(aggregate),
        "pts_english": pts["english"],
        "pts_core_maths": pts["core_maths"],
        "pts_biology": pts["biology"],
        "pts_chemistry": pts["chemistry"],
        "pts_physics": pts["physics"],
        "pts_elective_maths": pts["elective_maths"],
        "pts_integrated_science": pts["integrated_science"],
        "pts_social_studies": pts["social_studies"],
        "trait_analytical": traits["analytical"],
        "trait_empathy": traits["empathy"],
        "trait_practical": traits["practical"],
        "trait_creative": traits["creative"],
        "logic_accuracy": accuracies["logic"],
        "quant_accuracy": accuracies["quant"],
        "scientific_accuracy": accuracies["scientific"],
        "verbal_accuracy": accuracies["verbal"],
        "label_programme": label,
        "archetype": archetype,
        "band_pool": "eligible" if eligible else "stretch",
        "ability": ability,
    }


def main() -> None:
    programmes = _load_programmes()
    rows: list[dict] = []
    attempts = 0
    while len(rows) < N_STUDENTS and attempts < N_STUDENTS * 5:
        attempts += 1
        row = generate_row(RNG, programmes)
        if row:
            rows.append(row)

    df = pd.DataFrame(rows)
    # Ensure column order
    cols = FEATURE_COLUMNS + ["label_programme", "archetype", "band_pool", "ability"]
    df = df[cols]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"Wrote {len(df)} rows -> {OUT_CSV}")
    print(f"Unique labels: {df['label_programme'].nunique()}")
    print(df["label_programme"].value_counts().head(15).to_string())
    print(f"Aggregate mean: {df['aggregate'].mean():.1f}")


if __name__ == "__main__":
    main()
