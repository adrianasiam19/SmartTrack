"""Tests for KNUST Decision Tree alternate ranker (gate + soft teacher)."""

from ml_aspect.knust_dt.soft_label import programme_soft_score
from ml_aspect.knust_dt.predict import predict_knust_dt_alternate


def test_soft_score_prefers_health_for_bio_chem_profile():
    pts = {
        "english": 3,
        "core_maths": 3,
        "biology": 2,
        "chemistry": 2,
        "physics": 4,
        "elective_maths": 5,
        "integrated_science": 3,
        "social_studies": 4,
    }
    traits = {"analytical": 70, "empathy": 85, "practical": 40, "creative": 40}
    acc = {"logic": 60, "quant": 55, "scientific": 80, "verbal": 55}
    health = programme_soft_score(
        {"family": "Health Sciences", "cutoff": 9, "programme": "BSc Nursing"},
        aggregate=12,
        pts=pts,
        traits=traits,
        accuracies=acc,
    )
    eng = programme_soft_score(
        {"family": "Engineering", "cutoff": 10, "programme": "BSc Civil Engineering"},
        aggregate=12,
        pts=pts,
        traits=traits,
        accuracies=acc,
    )
    assert health > eng


def test_dt_predict_only_returns_eligible_or_stretch():
    features = {
        "aggregate": 14,
        "pts_english": 3,
        "pts_core_maths": 2,
        "pts_biology": 4,
        "pts_chemistry": 4,
        "pts_physics": 3,
        "pts_elective_maths": 2,
        "pts_integrated_science": 4,
        "pts_social_studies": 4,
        "trait_analytical": 80,
        "trait_empathy": 40,
        "trait_practical": 75,
        "trait_creative": 45,
        "logic_accuracy": 70,
        "quant_accuracy": 75,
        "scientific_accuracy": 60,
        "verbal_accuracy": 55,
    }
    knust = {
        "cycle": "2025/2026",
        "bands": {
            "eligible": [
                {
                    "programme": "BSc Civil Engineering",
                    "family": "Engineering",
                    "cutoff": 10,
                    "demand": "High",
                    "aggregate": 14,
                    "headroom": -4,
                },
                {
                    "programme": "BSc Industrial Engineering",
                    "family": "Engineering",
                    "cutoff": 16,
                    "demand": "Medium",
                    "aggregate": 14,
                    "headroom": 2,
                },
            ],
            "stretch": [
                {
                    "programme": "BSc Mechanical Engineering",
                    "family": "Engineering",
                    "cutoff": 10,
                    "demand": "High",
                    "aggregate": 14,
                    "headroom": -4,
                }
            ],
            "reach": [
                {
                    "programme": "MBChB Medicine",
                    "family": "Health Sciences",
                    "cutoff": 6,
                    "demand": "Very High",
                    "aggregate": 14,
                    "headroom": -8,
                }
            ],
        },
    }
    out = predict_knust_dt_alternate(features, knust_payload=knust, top_n=5)
    names = {r["programme"] for r in out}
    assert "MBChB Medicine" not in names
    assert names.issubset(
        {"BSc Civil Engineering", "BSc Industrial Engineering", "BSc Mechanical Engineering"}
    )
    assert all(r["role"] == "alternate" for r in out)
    assert all(r["eligibility_band"] in {"eligible", "stretch"} for r in out)
