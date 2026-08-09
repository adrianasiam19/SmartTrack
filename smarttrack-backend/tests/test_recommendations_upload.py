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


def test_recommendation_engine_returns_nearby_profile_programmes():
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
    assert "suitable_programmes" in result
    for rec in result["suitable_programmes"]:
        assert "why_recommended" in rec
        assert "score" not in rec
        assert 14 <= int(rec["cutoff"]) <= 16
        assert "Business" not in (rec.get("programme") or "")
    names = {r["programme"] for r in result["suitable_programmes"]}
    assert "MBChB Medicine" not in names
    for rec in result.get("competitive_programmes") or []:
        assert 11 <= int(rec["cutoff"]) < 14


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


def test_assess_waec_rejects_plain_grade_list():
    from app.assessment.academic_recommendations import (
        assess_waec_document,
        parse_grades_from_text,
    )

    text = """
    English Language B3
    Core Mathematics A1
    Integrated Science C4
    Social Studies B2
    Physics B3
    Chemistry C5
    """
    grades = parse_grades_from_text(text)
    assert len(grades) >= 4
    result = assess_waec_document(text, grades=grades)
    assert result["is_waec"] is False


def test_assess_waec_accepts_official_markers():
    from app.assessment.academic_recommendations import (
        assess_waec_document,
        parse_grades_from_text,
    )

    text = """
    WEST AFRICAN EXAMINATIONS COUNCIL
    WASSCE Statement of Results
    Candidate Number: 1234567
    English Language B3
    Core Mathematics A1
    Integrated Science C4
    Social Studies B2
    Physics B3
    Chemistry C5
    """
    grades = parse_grades_from_text(text)
    result = assess_waec_document(text, grades=grades)
    assert result["is_waec"] is True
    assert result["confidence"] >= 0.7


def test_extract_and_match_candidate_name():
    from app.assessment.academic_recommendations import (
        compare_candidate_to_profile,
        extract_candidate_name_from_text,
    )

    text = """
    WEST AFRICAN EXAMINATIONS COUNCIL
    Candidate Name: ASIAMAH YAW KWAME
    English Language B3
    """
    assert extract_candidate_name_from_text(text) == "ASIAMAH YAW KWAME"

    # Order / missing middle name still matches
    ok = compare_candidate_to_profile("Yaw Kwame Asiamah", "ASIAMAH YAW KWAME")
    assert ok["matched"] is True

    bad = compare_candidate_to_profile("Yaw Kwame Asiamah", "MENSAH KOFI")
    assert bad["matched"] is False
    assert bad["reason"] == "name_mismatch"

    missing = compare_candidate_to_profile("Yaw Kwame Asiamah", None)
    assert missing["matched"] is False
    assert missing["reason"] == "document_name_missing"

    short_profile = compare_candidate_to_profile("Yaw", "YAW KWAME ASIAMAH")
    assert short_profile["matched"] is False
    assert short_profile["reason"] == "profile_name_incomplete"


def test_extract_grades_uses_pypdf_text(monkeypatch):
    import asyncio
    from app.assessment import academic_recommendations as mod

    sample = (
        "WEST AFRICAN EXAMINATIONS COUNCIL\n"
        "WASSCE\n"
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


def test_analyze_rejects_non_waec_pdf_text(monkeypatch):
    import asyncio
    from app.assessment import academic_recommendations as mod

    sample = (
        "School Progress Report\n"
        "English Language B3\n"
        "Core Mathematics A1\n"
        "Integrated Science C4\n"
        "Social Studies B2\n"
        "Physics B3\n"
    )
    monkeypatch.setattr(mod, "extract_text_from_pdf", lambda _data: sample)

    result = asyncio.run(
        mod.analyze_academic_document(
            filename="report.pdf",
            content_type="application/pdf",
            data=b"%PDF-fake",
        )
    )
    assert result["waec"]["is_waec"] is False

