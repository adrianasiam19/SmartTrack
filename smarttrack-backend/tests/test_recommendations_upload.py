"""Tests for programme recommendation unlock after academic upload."""

from app.assessment.academic_recommendations import (
    merge_academic_upload_into_profile,
    programme_fallback_skills,
    validate_academic_file,
)
from app.assessment.recommendation_engine import RecommendationEngine


def test_validate_academic_file_accepts_pdf_and_rejects_exe():
    assert validate_academic_file("results.pdf", "application/pdf", 1200) is None
    assert validate_academic_file("photo.png", "image/png", 2200) is None
    assert validate_academic_file("virus.exe", "application/octet-stream", 100) is not None
    assert validate_academic_file("big.pdf", "application/pdf", 20 * 1024 * 1024) is not None


def test_programme_fallback_skills_for_science():
    skills = programme_fallback_skills("General Science")
    assert skills["Science"] > skills["Verbal"]


def test_recommendation_engine_works_without_irt_when_grades_present():
    engine = RecommendationEngine(
        skill_estimates={},
        behavioral_traits={},
        academic_grades=[
            {"subject": "Core Mathematics", "grade": "A1"},
            {"subject": "Physics", "grade": "B2"},
            {"subject": "Chemistry", "grade": "B3"},
        ],
        programme="General Science",
        learner_profile={"recommended_focus": "Strengthen scientific reasoning"},
    )
    result = engine.generate_recommendations()
    assert result["recommendations"]
    assert result["recommendations"][0]["fit_score"] >= result["recommendations"][-1]["fit_score"]
    assert result["grades_used"] == 3
    top = result["recommendations"][0]["programme_family"]
    assert top in {
        "Natural Sciences",
        "Engineering",
        "Health Sciences",
        "Computing & IT",
    }


def test_merge_academic_upload_preserves_existing_profile_fields():
    merged = merge_academic_upload_into_profile(
        {"recommended_focus": "Keep practicing logic"},
        filename="wassce.pdf",
        stored_name="abc_wassce.pdf",
        grades=[{"subject": "English Language", "grade": "C4"}],
    )
    assert merged["recommended_focus"] == "Keep practicing logic"
    assert merged["academic_upload"]["filename"] == "wassce.pdf"
    assert merged["academic_upload"]["grades_extracted"] is True
