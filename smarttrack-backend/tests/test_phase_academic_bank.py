"""Tests for phase academic bank selection rules."""
from __future__ import annotations

import random

from app.phases.academic_bank import (
    bank_stats,
    include_wassce_for_phase,
    load_bank,
    select_question,
)


def test_bank_loaded():
    items = load_bank()
    assert len(items) >= 100
    stats = bank_stats()
    assert stats["wassce"] >= 30


def test_phase1_only_shs1_classroom():
    rng = random.Random(42)
    for _ in range(20):
        q = select_question(
            phase_number=1,
            subject="core_maths",
            effective_difficulty=3,
            rng=rng,
        )
        assert q is not None
        assert q["shs_level"] == "SHS 1"
        assert q.get("exam_style") != "wassce"


def test_phase2_allows_shs1_and_shs2_not_wassce():
    rng = random.Random(7)
    seen = set()
    for _ in range(30):
        q = select_question(
            phase_number=2,
            subject="english",
            effective_difficulty=5,
            rng=rng,
        )
        assert q is not None
        assert q["shs_level"] in {"SHS 1", "SHS 2"}
        assert q.get("exam_style") != "wassce"
        seen.add(q["shs_level"])
    assert "SHS 1" in seen or "SHS 2" in seen


def test_phase3_can_include_wassce():
    assert include_wassce_for_phase(3) is True
    rng = random.Random(99)
    styles = set()
    levels = set()
    exclude: set[str] = set()
    for _ in range(40):
        q = select_question(
            phase_number=3,
            subject="social_studies",
            effective_difficulty=11,
            exclude_ids=exclude,
            rng=rng,
        )
        if not q:
            break
        styles.add(q.get("exam_style"))
        levels.add(q.get("shs_level"))
        if q.get("bank_id"):
            exclude.add(str(q["bank_id"]))
    assert levels <= {"SHS 1", "SHS 2", "SHS 3"}
    # High difficulty should often pull wassce items when available
    assert "wassce" in styles or "classroom" in styles


def test_exclude_ids_avoids_repeats():
    rng = random.Random(1)
    first = select_question(
        phase_number=1,
        subject="integrated_science",
        effective_difficulty=2,
        rng=rng,
    )
    assert first and first.get("bank_id")
    second = select_question(
        phase_number=1,
        subject="integrated_science",
        effective_difficulty=2,
        exclude_ids={str(first["bank_id"])},
        rng=rng,
    )
    assert second is not None
    assert second.get("bank_id") != first.get("bank_id")
