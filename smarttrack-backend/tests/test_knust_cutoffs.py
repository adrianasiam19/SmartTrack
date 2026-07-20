"""Tests for KNUST cut-off aggregate + eligibility boundaries."""

from app.recommendations.cutoffs import (
    apply_cutoff_boundaries,
    compute_wassce_aggregate,
    eligibility_band,
    load_knust_cutoffs,
)


def test_load_knust_cutoffs_has_three_families():
    data = load_knust_cutoffs()
    assert data["university"] == "KNUST"
    families = {p["family"] for p in data["programmes"]}
    assert families == {"Health Sciences", "Engineering", "Science"}
    assert len(data["programmes"]) == 47


def test_aggregate_uses_english_maths_and_best_four():
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
    result = compute_wassce_aggregate(grades)
    assert result["complete"] is True
    assert result["grades_counted"] == 6
    # A1(1) + B3(3) + A1 elective(1) + B2(2) + B3(3) + C4(4) = 14
    assert result["aggregate"] == 14


def test_eligibility_bands():
    assert eligibility_band(6, 6, "Very High") == "eligible"
    assert eligibility_band(7, 6, "Very High") == "stretch"
    assert eligibility_band(9, 6, "Very High") == "reach"
    assert eligibility_band(None, 6) == "unknown"


def test_apply_boundaries_puts_medicine_out_of_reach_for_mid_aggregate():
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
    # Aggregate 14 — clears mid cutoffs, not Medicine (6)
    out = apply_cutoff_boundaries(
        grades=grades,
        family_fit_scores={"Health Sciences": 90, "Engineering": 70, "Natural Sciences": 60},
    )
    assert out["aggregate"]["aggregate"] == 14
    eligible_names = {p["programme"] for p in out["bands"]["eligible"]}
    assert "MBChB Medicine" not in eligible_names
    assert any(p["cutoff"] >= 14 for p in out["bands"]["eligible"])
    reach_names = {p["programme"] for p in out["bands"]["reach"]}
    assert "MBChB Medicine" in reach_names
