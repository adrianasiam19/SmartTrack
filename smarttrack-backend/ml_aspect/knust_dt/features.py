"""Shared feature schema for the KNUST Decision Tree ranker."""
from __future__ import annotations

FEATURE_COLUMNS: list[str] = [
    "aggregate",
    "pts_english",
    "pts_core_maths",
    "pts_biology",
    "pts_chemistry",
    "pts_physics",
    "pts_elective_maths",
    "pts_integrated_science",
    "pts_social_studies",
    "trait_analytical",
    "trait_empathy",
    "trait_practical",
    "trait_creative",
    "logic_accuracy",
    "quant_accuracy",
    "scientific_accuracy",
    "verbal_accuracy",
]

MISSING_SUBJECT_POINTS = 9.0
