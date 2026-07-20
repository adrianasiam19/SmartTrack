"""Tests for post-phase psychometric checkpoint selection."""

from __future__ import annotations

import uuid

import pytest

from app.psychometrics.selection import (
    CHECKPOINT_CATEGORIES,
    _hydrate_llm_picks,
    _parse_bank_id_list,
    select_checkpoint_questions,
)


class _FakeOption:
    def __init__(self, label: str, text: str):
        self.label = label
        self.text = text
        self.id = ord(label)


class _FakeQuestion:
    def __init__(self, qid: int, number: int, category: str, text: str, bank_id: str | None = None):
        self.id = qid
        self.bank_id = bank_id or f"qb-{qid:03d}"
        self.number = number
        self.category = category
        self.text = text
        self.options = [
            _FakeOption("A", "One"),
            _FakeOption("B", "Two"),
            _FakeOption("C", "Three"),
            _FakeOption("D", "Four"),
        ]


class _FakePhase:
    def __init__(self):
        self.number = 1
        self.name = "Phase 1"


class _FakeUser:
    programme = "General Science"
    shs_level = "SHS 1"


class _Result:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return self._rows if isinstance(self._rows, list) else [self._rows]

    def scalar_one_or_none(self):
        if isinstance(self._rows, list):
            return self._rows[0] if self._rows else None
        return self._rows


class _DB:
    """Minimal async DB stub: questions → history → phase → user."""

    def __init__(self, questions, history=None):
        self.questions = questions
        self.history = history or []
        self._calls = 0

    async def execute(self, _query):
        self._calls += 1
        if self._calls == 1:
            return _Result(self.questions)
        if self._calls == 2:
            return _Result(self.history)
        if self._calls == 3:
            return _Result(_FakePhase())
        return _Result(_FakeUser())


def _bank_with_all_categories() -> list[_FakeQuestion]:
    questions: list[_FakeQuestion] = []
    qid = 1
    for category in CHECKPOINT_CATEGORIES:
        for i in range(3):
            questions.append(
                _FakeQuestion(
                    qid,
                    qid,
                    category,
                    f"{category} question {i + 1}",
                )
            )
            qid += 1
    return questions


@pytest.mark.asyncio
async def test_checkpoint_selects_eight_distinct_categories(monkeypatch):
    monkeypatch.setattr(
        "app.psychometrics.selection.settings.PSYCHO_CHECKPOINT_COUNT",
        8,
    )

    async def no_llm(**_kwargs):
        return []

    monkeypatch.setattr(
        "app.psychometrics.selection._llm_select_bank_ids",
        no_llm,
    )
    questions = _bank_with_all_categories()
    selected = await select_checkpoint_questions(
        db=_DB(questions),
        user_id=uuid.uuid4(),
        phase_id=1,
    )
    assert len(selected) == 8
    categories = [q.category for q in selected]
    assert len(set(categories)) == 8
    assert set(categories).issubset(set(CHECKPOINT_CATEGORIES))


@pytest.mark.asyncio
async def test_checkpoint_uses_llm_picks_when_valid(monkeypatch):
    monkeypatch.setattr(
        "app.psychometrics.selection.settings.PSYCHO_CHECKPOINT_COUNT",
        8,
    )
    questions = _bank_with_all_categories()
    # One bank_id from each of the first 8 categories.
    picks = []
    for category in CHECKPOINT_CATEGORIES[:8]:
        picks.append(next(q.bank_id for q in questions if q.category == category))

    async def fake_llm(**_kwargs):
        return picks

    monkeypatch.setattr(
        "app.psychometrics.selection._llm_select_bank_ids",
        fake_llm,
    )
    selected = await select_checkpoint_questions(
        db=_DB(questions),
        user_id=uuid.uuid4(),
        phase_id=1,
    )
    assert [q.bank_id for q in selected] == picks
    assert [q.category for q in selected] == CHECKPOINT_CATEGORIES[:8]


@pytest.mark.asyncio
async def test_checkpoint_prefers_uncovered_categories(monkeypatch):
    monkeypatch.setattr(
        "app.psychometrics.selection.settings.PSYCHO_CHECKPOINT_COUNT",
        8,
    )

    async def no_llm(**_kwargs):
        return []

    monkeypatch.setattr(
        "app.psychometrics.selection._llm_select_bank_ids",
        no_llm,
    )
    questions = _bank_with_all_categories()
    covered = CHECKPOINT_CATEGORIES[:8]
    history = []
    for category in covered:
        first = next(q for q in questions if q.category == category)

        class _Hist:
            question_id = first.id
            phase_id = 1

        history.append(_Hist())

    selected = await select_checkpoint_questions(
        db=_DB(questions, history=history),
        user_id=uuid.uuid4(),
        phase_id=2,
    )
    selected_cats = {q.category for q in selected}
    assert len(selected_cats) == 8
    assert len(selected_cats & set(covered)) <= 2
    assert len(selected_cats - set(covered)) >= 6


def test_parse_bank_id_list_from_json():
    assert _parse_bank_id_list('["qb-001", "qb-002"]') == ["qb-001", "qb-002"]
    assert _parse_bank_id_list('Here you go:\n["qb-010"]\n') == ["qb-010"]


def test_hydrate_llm_picks_dedupes_categories():
    q1 = _FakeQuestion(1, 1, "Curiosity", "A", "qb-001")
    q2 = _FakeQuestion(2, 2, "Curiosity", "B", "qb-002")
    q3 = _FakeQuestion(3, 3, "Creativity", "C", "qb-003")
    by_id = {"qb-001": q1, "qb-002": q2, "qb-003": q3}
    picked = _hydrate_llm_picks(
        ["qb-001", "qb-002", "qb-003"],
        by_bank_id=by_id,
        count=8,
    )
    assert [q.bank_id for q in picked] == ["qb-001", "qb-003"]


def test_checkpoint_categories_cover_full_tagged_bank():
    assert len(CHECKPOINT_CATEGORIES) == 20
    assert "Learning Preferences" in CHECKPOINT_CATEGORIES
    assert "Research Interest" in CHECKPOINT_CATEGORIES
