"""Learner-facing presentation helpers."""

from app.recommendations.presentation import (
    build_psychometric_prose,
    is_internal_programme_label,
    select_suitable_and_competitive,
    sanitize_phase_suggestions,
)


def test_psych_prose_hides_internal_keys():
    prose = build_psychometric_prose(
        {
            "analytical": 5,
            "curiosity": 4,
            "business_law": 9,
            "medicine_health": 8,
        }
    )
    assert "business" not in prose.lower() or "Business Law" not in prose
    assert "medicine_health" not in prose
    assert "analytical" in prose.lower() or "curiosity" in prose.lower()


def test_sanitize_drops_affinity_labels():
    cleaned = sanitize_phase_suggestions(
        [
            {"programme": "Business Law", "score": 0.96},
            {"programme": "BSc Nursing", "cutoff": 9},
            {"programme": "Arts Media", "score": 0.2},
        ]
    )
    names = {c["programme"] for c in cleaned}
    assert "Business Law" not in names
    assert "Arts Media" not in names
    assert "BSc Nursing" in names
    assert all("score" not in c for c in cleaned)


def test_nearby_aggregate_filters_far_cutoffs():
    grades = [
        {"subject": "English Language", "grade": "B3"},
        {"subject": "Core Mathematics", "grade": "A1"},
        {"subject": "Integrated Science", "grade": "C4"},
        {"subject": "Social Studies", "grade": "B2"},
        {"subject": "Physics", "grade": "B3"},
        {"subject": "Chemistry", "grade": "C5"},
        {"subject": "Biology", "grade": "C6"},
        {"subject": "Elective Mathematics", "grade": "A1"},
    ]
    # Aggregate 14 from existing cutoff tests
    out = select_suitable_and_competitive(
        grades=grades,
        family_fit_scores={
            "Health Sciences": 40,
            "Engineering": 90,
            "Natural Sciences": 70,
        },
        nearby_range=2,
        competitive_range=3,
        limit=10,
    )
    agg = out["aggregate"]["aggregate"]
    assert agg == 14
    for row in out["suitable"]:
        assert agg <= int(row["cutoff"]) <= agg + 2
    for row in out["competitive"]:
        assert agg - 3 <= int(row["cutoff"]) < agg
    assert not is_internal_programme_label("BSc Civil Engineering")
