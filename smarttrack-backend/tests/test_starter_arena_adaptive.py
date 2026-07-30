"""Tests for the adaptive Starter Arena engine."""

from app.assessment.starter_arena import (
    PSYCHOMETRIC_CATEGORY_PLAN,
    _balanced_psychometric_questions,
    _is_unique_question,
    _questions_are_similar,
    build_adaptive_cognitive_prompt,
    generate_starter_session,
)
from app.assessment.psychometric_cards import PSYCHOMETRIC_CARDS
from app.users.schemas import UserPublic


class _FakeCard:
    def __init__(self, card_id: str, question: str, options):
        self.card_id = card_id
        self.question = question
        self.options = options


def test_user_public_exposes_learner_profile():
    assert "learner_profile" in UserPublic.model_fields


def test_similar_questions_are_detected():
    assert _questions_are_similar(
        "When you study a new topic, what helps you most?",
        "When you study a new topic what helps you most?",
    )
    assert not _questions_are_similar(
        "How do you prefer to lead a team project?",
        "Which science topic do you find most interesting?",
    )


def test_unique_question_helper_rejects_near_duplicates():
    existing = ["Imagine your class has no electricity for a presentation. What would you do?"]
    assert not _is_unique_question(
        "Imagine your class has no electricity for a presentation. What would you do first?",
        existing,
    )
    assert _is_unique_question(
        "Three classmates give different explanations for a delay. What would you check first?",
        existing,
    )


def test_balanced_psychometric_selection_is_unique_and_varied():
    cards = [
        _FakeCard(
            card["id"],
            card["question"],
            card["options"],
        )
        for card in PSYCHOMETRIC_CARDS[:120]
    ]
    selected = _balanced_psychometric_questions(cards, count=4, seen_card_ids=set())
    assert len(selected) == 4
    texts = [item["question"] for item in selected]
    assert len(set(texts)) == 4
    categories = [item["category"] for item in selected]
    # Each of the 4 should come from a different topic/category.
    assert len(set(categories)) == 4
    assert all(item["source"] == "database" for item in selected)
    assert all(item["type"] == "psychometric" for item in selected)
    # Previously answered cards must never reappear.
    blocked = {item["id"].removeprefix("psych_") for item in selected[:2]}
    selected_again = _balanced_psychometric_questions(
        cards, count=4, seen_card_ids=blocked
    )
    assert not any(item["id"].removeprefix("psych_") in blocked for item in selected_again)


def test_adaptive_prompt_contains_rich_context():
    prompt = build_adaptive_cognitive_prompt(
        count=4,
        shs_level="SHS 2",
        total_assessment_questions=8,
        existing_questions=[
            "When studying a new topic, what helps you most?",
            "How do you usually make difficult decisions?",
        ],
        covered_categories=["Learning Preferences", "Decision Making", "Curiosity", "Creativity"],
        skill_plan=[
            "logical reasoning",
            "communication reasoning",
            "logical reasoning",
            "communication reasoning",
        ],
        format_plan=["short-response", "best-solution", "scenario", "multiple-choice"],
    )
    assert "Student SHS level: SHS 2" in prompt
    assert "Learning Preferences" in prompt
    assert "Decision Making" in prompt
    assert "logical reasoning" in prompt
    assert "communication reasoning" in prompt
    assert "When studying a new topic, what helps you most?" in prompt
    assert "NOT an examination" in prompt
    assert "identical or substantially similar" in prompt
    assert "moderately challenging" in prompt
    assert "two thinking questions" in prompt


def test_category_plan_covers_core_discovery_areas():
    for category in (
        "Learning Preferences",
        "Curiosity",
        "Creativity",
        "Leadership",
        "Teamwork",
        "Decision Making",
    ):
        assert category in PSYCHOMETRIC_CATEGORY_PLAN


async def test_generate_starter_session_alternates_sources(monkeypatch):
    class _Result:
        def __init__(self, rows):
            self._rows = rows

        def scalars(self):
            return self

        def all(self):
            return self._rows

        def fetchall(self):
            return self._rows

    class _DB:
        async def execute(self, _query):
            # First call: psychometric cards. Second call: prior responses.
            if not hasattr(self, "_calls"):
                self._calls = 0
            self._calls += 1
            if self._calls == 1:
                cards = [
                    _FakeCard(card["id"], card["question"], card["options"])
                    for card in PSYCHOMETRIC_CARDS[:80]
                ]
                return _Result(cards)
            return _Result([])

    async def fake_cognitive(**kwargs):
        count = kwargs["count"]
        return [
            {
                "id": f"cognitive_ai_{index + 1}",
                "type": "cognitive",
                "source": "llm",
                "cognitive_skill": "logical reasoning",
                "format": "scenario",
                "domain": "Logical Reasoning",
                "question": f"Unique cognitive discovery question number {index + 1}?",
                "options": {"A": "One", "B": "Two", "C": "Three", "D": "Four"},
                "correct_key": None,
                "explanation": "Thanks",
            }
            for index in range(count)
        ]

    monkeypatch.setattr(
        "app.assessment.starter_arena._generate_adaptive_cognitive_questions",
        fake_cognitive,
    )

    session = await generate_starter_session(
        db=_DB(),
        user_id="00000000-0000-0000-0000-000000000001",
        shs_level="SHS 1",
        programme="General Science",
        psychometric_count=4,
        academic_count=4,
    )

    questions = session["questions"]
    assert session["total_count"] == 8
    # Pattern: 2 LLM thinking → 2 psychometric → repeat
    assert [q["type"] for q in questions] == [
        "cognitive",
        "cognitive",
        "psychometric",
        "psychometric",
        "cognitive",
        "cognitive",
        "psychometric",
        "psychometric",
    ]
    assert [q["source"] for q in questions if q["type"] == "psychometric"] == [
        "database"
    ] * 4
    assert all(q["source"] == "llm" for q in questions if q["type"] == "cognitive")
    psych_categories = [q["category"] for q in questions if q["type"] == "psychometric"]
    assert len(set(psych_categories)) == 4
    texts = [q["question"] for q in questions]
    assert len(texts) == len(set(texts))
