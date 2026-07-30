"""
generate_data.py
────────────────
Synthetic training data generator for the ATLAS career-recommendation model.

DESIGN PRINCIPLE: every synthetic student has an underlying "true" programme
affinity. All other features (WASSCE grades, psychometric traits, challenge
performance) are then generated CONSISTENTLY with that affinity, plus
realistic noise. This is what makes the model learn transferable patterns
instead of memorising noise — critical since this synthetic data will later
be supplemented or replaced with real ATLAS user data using the exact same
feature columns.

GENERATION ORDER (each stage depends on the previous one):
  1. Pick a target programme (the label)
  2. Track (Science/Arts/Business) is implied by the programme
  3. WASSCE grades are generated to fit that programme's real entry profile
     (e.g. Medicine -> high Biology/Chemistry/Physics)
  4. Psychometric traits are generated to fit the programme's typical
     personality profile (e.g. Medicine -> high analytical + high empathy)
  5. Challenge performance (Logic/Quant/Verbal/Scientific accuracy) is
     generated to correlate with both WASSCE grades AND psychometric traits
     — mimicking how a real student's in-app performance would reflect
     their underlying academic strengths.

Output: data/synthetic_students.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N_STUDENTS = 6000

OUTPUT_PATH = Path(__file__).parent / "data" / "synthetic_students.csv"

# ─────────────────────────────────────────────────────────────────────────
# 1. PROGRAMME DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────
# Mirrors smarttrack-frontend/app/lib/ghanaPrograms.ts — keep these in sync
# if the frontend catalogue changes.

PROGRAMMES = {
    # id: (track, {wassce subject: target_mean_grade 1-9 WAEC scale (1=best)})
    "medicine-surgery":       ("Science", {"biology": 1.5, "chemistry": 1.5, "physics": 2.0, "core_maths": 2.0, "english": 2.0}),
    "engineering-civil":      ("Science", {"elective_maths": 1.5, "physics": 1.5, "chemistry": 3.0, "core_maths": 1.5, "english": 3.0}),
    "computer-science":       ("Science", {"elective_maths": 1.5, "physics": 2.5, "chemistry": 3.5, "core_maths": 1.5, "english": 2.5}),
    "pharmacy":               ("Science", {"chemistry": 1.5, "biology": 1.5, "physics": 3.0, "core_maths": 2.5, "english": 2.5}),
    "nursing":                ("Science", {"biology": 2.0, "chemistry": 2.5, "physics": 4.0, "core_maths": 3.0, "english": 2.5}),
    "electrical-engineering": ("Science", {"elective_maths": 1.5, "physics": 1.5, "chemistry": 3.0, "core_maths": 1.5, "english": 3.0}),
    "agriculture":            ("Science", {"biology": 2.0, "chemistry": 3.0, "physics": 4.0, "core_maths": 3.5, "english": 3.5}),
    "law":                    ("Arts",    {"literature": 1.5, "government": 2.0, "history": 2.5, "core_maths": 4.0, "english": 1.5}),
    "journalism":             ("Arts",    {"literature": 1.5, "government": 2.5, "history": 3.0, "core_maths": 4.5, "english": 1.5}),
    "education":              ("Arts",    {"literature": 2.5, "government": 3.0, "history": 3.0, "core_maths": 3.5, "english": 2.5}),
    "psychology":             ("Arts",    {"literature": 2.5, "government": 3.0, "biology": 3.0, "core_maths": 3.5, "english": 2.0}),
    "accounting":             ("Business", {"financial_accounting": 1.5, "economics": 2.0, "elective_maths": 2.5, "core_maths": 2.0, "english": 3.0}),
    "banking-finance":        ("Business", {"economics": 1.5, "financial_accounting": 2.0, "elective_maths": 2.0, "core_maths": 1.5, "english": 2.5}),
    "economics":              ("Business", {"economics": 1.5, "elective_maths": 1.5, "financial_accounting": 3.0, "core_maths": 1.5, "english": 2.5}),
    "marketing":              ("Business", {"business_management": 2.0, "economics": 2.5, "financial_accounting": 3.0, "core_maths": 3.5, "english": 2.5}),
    "public-administration":  ("Business", {"government": 2.0, "economics": 2.5, "history": 3.0, "core_maths": 3.5, "english": 2.5}),
}

PROGRAMME_IDS = list(PROGRAMMES.keys())

# Every possible WASSCE subject across all programmes — students get a
# score on all of them, even if a given programme doesn't "care" about it
# (those get generated near the track's average, not a strong target).
ALL_SUBJECTS = sorted({
    subj for _, subjects in PROGRAMMES.values() for subj in subjects
} | {"core_maths", "english", "integrated_science", "social_studies"})

# ─────────────────────────────────────────────────────────────────────────
# 2. PSYCHOMETRIC TRAIT PROFILES PER PROGRAMME
# ─────────────────────────────────────────────────────────────────────────
# Traits are 0-100 scale. These are target MEANS — actual generation adds
# per-student noise. Traits: analytical, creative, social, practical,
# leadership, empathy.

TRAIT_NAMES = ["analytical", "creative", "social", "practical", "leadership", "empathy"]

PROGRAMME_TRAITS = {
    "medicine-surgery":       {"analytical": 80, "creative": 45, "social": 65, "practical": 70, "leadership": 60, "empathy": 85},
    "engineering-civil":      {"analytical": 85, "creative": 55, "social": 40, "practical": 85, "leadership": 55, "empathy": 35},
    "computer-science":       {"analytical": 88, "creative": 65, "social": 35, "practical": 70, "leadership": 45, "empathy": 30},
    "pharmacy":               {"analytical": 80, "creative": 40, "social": 55, "practical": 75, "leadership": 45, "empathy": 60},
    "nursing":                {"analytical": 60, "creative": 35, "social": 75, "practical": 80, "leadership": 50, "empathy": 90},
    "electrical-engineering": {"analytical": 85, "creative": 50, "social": 35, "practical": 88, "leadership": 50, "empathy": 30},
    "agriculture":            {"analytical": 60, "creative": 45, "social": 50, "practical": 85, "leadership": 50, "empathy": 50},
    "law":                    {"analytical": 75, "creative": 50, "social": 75, "practical": 40, "leadership": 80, "empathy": 55},
    "journalism":             {"analytical": 55, "creative": 80, "social": 85, "practical": 45, "leadership": 60, "empathy": 65},
    "education":              {"analytical": 55, "creative": 60, "social": 80, "practical": 55, "leadership": 65, "empathy": 80},
    "psychology":             {"analytical": 65, "creative": 55, "social": 80, "practical": 40, "leadership": 50, "empathy": 90},
    "accounting":             {"analytical": 80, "creative": 30, "social": 40, "practical": 65, "leadership": 45, "empathy": 30},
    "banking-finance":        {"analytical": 82, "creative": 35, "social": 55, "practical": 55, "leadership": 65, "empathy": 35},
    "economics":              {"analytical": 85, "creative": 40, "social": 50, "practical": 50, "leadership": 60, "empathy": 35},
    "marketing":              {"analytical": 55, "creative": 80, "social": 85, "practical": 45, "leadership": 70, "empathy": 60},
    "public-administration":  {"analytical": 65, "creative": 40, "social": 75, "practical": 50, "leadership": 80, "empathy": 60},
}

# ─────────────────────────────────────────────────────────────────────────
# 3. CHALLENGE DOMAIN MAPPING
# ─────────────────────────────────────────────────────────────────────────
# Maps to ATLAS's 4 arenas: Logic, Quantitative, Verbal, Scientific.
# Accuracy (0-100%) per arena correlates with BOTH WASSCE grades AND traits.

ARENAS = ["logic_accuracy", "quant_accuracy", "verbal_accuracy", "scientific_accuracy"]


def grade_to_strength(grade: float) -> float:
    """WAEC grade is 1 (best) to 9 (worst) — invert to a 0-1 strength score."""
    return np.clip((9 - grade) / 8, 0, 1)


def generate_student(programme_id: str, rng: np.random.Generator) -> dict:
    track, subject_targets = PROGRAMMES[programme_id]
    trait_targets = PROGRAMME_TRAITS[programme_id]

    row = {"programme": programme_id, "track": track}

    # ── WASSCE grades: subjects this programme cares about get pulled
    # toward the target mean; everything else gets a mild track-average. ──
    track_baseline = {"Science": 4.0, "Arts": 4.2, "Business": 4.0}[track]
    for subject in ALL_SUBJECTS:
        target = subject_targets.get(subject, track_baseline)
        noise = rng.normal(0, 0.9)
        grade = np.clip(round(target + noise), 1, 9)
        row[f"wassce_{subject}"] = grade

    # ── Psychometric traits: noisy draw around the programme's profile ──
    for trait in TRAIT_NAMES:
        target = trait_targets[trait]
        noise = rng.normal(0, 10)
        row[f"trait_{trait}"] = float(np.clip(target + noise, 0, 100))

    # ── Challenge performance: blend of relevant WASSCE strength + traits ──
    maths_strength = grade_to_strength(
        row.get("wassce_elective_maths", row["wassce_core_maths"])
    )
    science_strength = np.mean([
        grade_to_strength(row.get(f"wassce_{s}", track_baseline))
        for s in ("biology", "chemistry", "physics")
        if f"wassce_{s}" in row
    ]) if track == "Science" else grade_to_strength(track_baseline)
    verbal_strength = grade_to_strength(row["wassce_english"])
    analytical_norm = row["trait_analytical"] / 100

    row["logic_accuracy"] = float(np.clip(
        100 * (0.5 * analytical_norm + 0.3 * maths_strength + rng.normal(0, 0.08)), 0, 100
    ))
    row["quant_accuracy"] = float(np.clip(
        100 * (0.7 * maths_strength + 0.2 * analytical_norm + rng.normal(0, 0.08)), 0, 100
    ))
    row["verbal_accuracy"] = float(np.clip(
        100 * (0.6 * verbal_strength + 0.2 * (row["trait_creative"] / 100) + rng.normal(0, 0.08)), 0, 100
    ))
    row["scientific_accuracy"] = float(np.clip(
        100 * (0.6 * science_strength + 0.3 * analytical_norm + rng.normal(0, 0.08)), 0, 100
    ))

    # ── Engagement features — loosely correlated with overall ability,
    # but with enough independent noise that they're not pure leakage. ──
    ability_avg = np.mean([row[a] for a in ARENAS]) / 100
    row["xp"] = int(np.clip(rng.normal(400 + ability_avg * 600, 250), 0, 6000))
    row["streak_days"] = int(np.clip(rng.normal(5 + ability_avg * 15, 6), 0, 90))

    return row


def main():
    rows = []
    for _ in range(N_STUDENTS):
        programme_id = RNG.choice(PROGRAMME_IDS)
        rows.append(generate_student(programme_id, RNG))

    df = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Generated {len(df)} synthetic students -> {OUTPUT_PATH}")
    print(f"\nProgramme distribution:\n{df['programme'].value_counts()}")
    print(f"\nColumns ({len(df.columns)}): {list(df.columns)}")


if __name__ == "__main__":
    main()
