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


def test_recommendation_engine_requires_grades():
    engine = RecommendationEngine(
        skill_estimates={},
        behavioral_traits={},
        academic_grades=[],
        programme="General Science",
    )
    result = engine.generate_recommendations()
    assert result["recommendations"] == []
    assert result["error"] == "grades_required"
    assert result["knust"] is None


def test_recommendation_engine_returns_only_knust_programmes():
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
    engine = RecommendationEngine(
        skill_estimates={},
        behavioral_traits={},
        academic_grades=grades,
        programme="General Science",
        learner_profile={"recommended_focus": "Strengthen scientific reasoning"},
    )
    result = engine.generate_recommendations()
    assert result["grades_used"] == 8
    assert result["knust"] is not None
    assert result["knust"]["aggregate"]["aggregate"] == 14
    assert result["recommendations"]
    for rec in result["recommendations"]:
        assert rec["source"] == "knust_cutoffs"
        assert rec["university"] == "KNUST"
        assert rec["eligibility_band"] in {"eligible", "stretch"}
        assert "Business" not in (rec.get("programme") or "")
        assert rec.get("programme_family") not in {
            "Business & Economics",
            "Law & Humanities",
            "Education & Social Sciences",
        }
    # Medicine (cutoff 6) must not appear as eligible for aggregate 14
    names = {r["programme"] for r in result["recommendations"]}
    assert "MBChB Medicine" not in names


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


def test_parse_grades_from_wassce_text():
    from app.assessment.academic_recommendations import parse_grades_from_text

    text = """
    WEST AFRICAN SENIOR SCHOOL CERTIFICATE EXAMINATION
    Candidate Name: TEST STUDENT
    English Language .......... B3
    Core Mathematics A1
    Integrated Science: C4
    Social Studies - B2
    Physics B3
    Chemistry C5
    Biology C6
    Elective Mathematics A1
    """
    grades = parse_grades_from_text(text)
    by_subject = {g["subject"]: g["grade"] for g in grades}
    assert by_subject["English Language"] == "B3"
    assert by_subject["Core Mathematics"] == "A1"
    assert by_subject["Integrated Science"] == "C4"
    assert by_subject["Social Studies"] == "B2"
    assert by_subject["Physics"] == "B3"
    assert by_subject["Chemistry"] == "C5"
    assert by_subject["Biology"] == "C6"
    assert by_subject["Elective Mathematics"] == "A1"


def test_extract_grades_uses_pypdf_text(monkeypatch):
    import asyncio
    from app.assessment import academic_recommendations as mod

    sample = (
        "English Language B3\n"
        "Core Mathematics A1\n"
        "Integrated Science C4\n"
        "Social Studies B2\n"
        "Physics B3\n"
        "Chemistry C5\n"
        "Biology C6\n"
        "Elective Mathematics A1\n"
    )
    monkeypatch.setattr(mod, "extract_text_from_pdf", lambda _data: sample)

    grades = asyncio.run(
        mod.extract_grades_with_ai(
            filename="wassce.pdf",
            content_type="application/pdf",
            data=b"%PDF-fake",
        )
    )
    assert len(grades) >= 6
    subjects = {g["subject"] for g in grades}
    assert "Core Mathematics" in subjects
    assert "English Language" in subjects

