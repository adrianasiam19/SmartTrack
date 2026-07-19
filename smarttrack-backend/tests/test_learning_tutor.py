import pytest
from fastapi import HTTPException

from app.assessment.models import CurriculumLesson
from app.learning.router import _is_in_scope, _scope_for, _search_score
from app.learning.service import _parse_lesson_json, build_grounding_text
from app.users.models import User


def make_user(level: str, programme: str = "General Science") -> User:
    return User(
        email=f"{level.replace(' ', '').lower()}@example.com",
        full_name="Curriculum Tester",
        password_hash="unused",
        shs_level=level,
        programme=programme,
    )


def make_lesson(level: str = "SHS 1") -> CurriculumLesson:
    return CurriculumLesson(
        curriculum_id="coremath-number-systems",
        title="Number Systems",
        subject="Core Mathematics",
        programme="Both",
        shs_levels=[level],
        unit_id="core-maths",
        difficulty=1,
        estimated_minutes=10,
        xp_reward=10,
        source_content={"steps": [{"content": "Natural numbers begin at one."}]},
        search_text="number systems natural numbers integers",
        ai_content_by_level={},
    )


def test_scope_accepts_only_shs_1_and_shs_2():
    assert _scope_for(make_user("SHS 1")) == ("SHS 1", "Science")
    assert _scope_for(make_user("SHS 2", "General Arts")) == ("SHS 2", "Arts")

    with pytest.raises(HTTPException) as error:
        _scope_for(make_user("SHS 3"))
    assert error.value.status_code == 403


def test_lesson_scope_blocks_other_levels_and_programmes():
    science_lesson = make_lesson("SHS 1")
    science_lesson.programme = "Science"

    assert _is_in_scope(science_lesson, "SHS 1", "Science")
    assert not _is_in_scope(science_lesson, "SHS 2", "Science")
    assert not _is_in_scope(science_lesson, "SHS 1", "Arts")


def test_search_supports_partial_and_misspelled_topic_names():
    lesson = make_lesson()
    assert _search_score("number", lesson) >= 0.9
    assert _search_score("numbr systms", lesson) >= 0.48
    assert _search_score("natural integers", lesson) >= 0.48


def test_grounding_removes_administrative_headings():
    source = {
        "steps": [
            {"content": "Learning Objectives\nUnderstand integers"},
            {"content": "Publisher Notes\nIntegers include negative whole numbers."},
        ]
    }
    grounding = build_grounding_text(source)
    assert "Learning Objectives" not in grounding
    assert "Publisher Notes" not in grounding
    assert "Understand integers" in grounding
    assert "negative whole numbers" in grounding


def test_ai_lesson_requires_every_teaching_section():
    valid = {
        "topic_title": "Number Systems",
        "simple_introduction": "Numbers help us count.",
        "main_explanation": "Natural numbers begin at one.",
        "step_by_step_examples": [
            {"title": "Classify 5", "steps": ["5 is positive"], "answer": "Natural"}
        ],
        "real_life_applications": ["Counting items"],
        "important_points": ["Zero is a whole number"],
        "common_mistakes": ["Do not call every integer natural"],
        "short_summary": "Number sets group related numbers.",
    }
    assert _parse_lesson_json(f"```json\n{__import__('json').dumps(valid)}\n```") == valid

    invalid = {**valid}
    invalid.pop("common_mistakes")
    with pytest.raises(Exception):
        _parse_lesson_json(__import__("json").dumps(invalid))
