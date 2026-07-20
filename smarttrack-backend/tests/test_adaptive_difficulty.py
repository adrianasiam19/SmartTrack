"""Unit tests for adaptive difficulty clamps / EMA / nudge / level budgets."""
from app.phases.adaptive import (
    AdaptiveConfig,
    adaptive_subject_mix,
    bump_adjustment_if_strong,
    effective_difficulty,
    expand_subject_queue,
    level_question_count,
    next_adjustment,
    normalize_question_text,
    should_nudge_learning,
    subject_mix_for_level,
    update_rolling_accuracy,
    update_weak_streak,
)
import random


def test_effective_difficulty_respects_phase_floor():
    cfg = AdaptiveConfig(difficulty_min=1, difficulty_max=15)
    assert effective_difficulty(5, -10, phase_floor=1, cfg=cfg) == 1
    assert effective_difficulty(5, -10, phase_floor=3, cfg=cfg) == 3


def test_effective_difficulty_clamps_max():
    cfg = AdaptiveConfig(difficulty_min=1, difficulty_max=15)
    assert effective_difficulty(10, 20, phase_floor=1, cfg=cfg) == 15


def test_next_adjustment_never_decreases_on_low_accuracy():
    cfg = AdaptiveConfig(low_accuracy=0.5, high_accuracy=0.6, adj_step=1)
    assert next_adjustment(0, 0.2, phase_floor=1, baseline=5, cfg=cfg) == 0
    assert next_adjustment(2, 0.1, phase_floor=1, baseline=5, cfg=cfg) == 2


def test_next_adjustment_increases_on_high_accuracy():
    cfg = AdaptiveConfig(low_accuracy=0.5, high_accuracy=0.6, adj_step=1)
    assert next_adjustment(0, 0.9, phase_floor=1, baseline=5, cfg=cfg) == 1


def test_bump_adjustment_if_strong():
    cfg = AdaptiveConfig(adj_step=1, difficulty_max=15)
    assert bump_adjustment_if_strong(0, 0.8, phase_floor=1, baseline=5, cfg=cfg) == 1
    assert bump_adjustment_if_strong(0, 0.2, phase_floor=1, baseline=5, cfg=cfg) == 0


def test_level_question_count_ramp():
    assert level_question_count(1) == 5
    assert level_question_count(5) == 5
    assert level_question_count(6) == 6
    assert level_question_count(7) == 6
    assert level_question_count(8) == 10
    assert level_question_count(10) == 10


def test_subject_mix_for_level_totals():
    acc = {
        "english": 0.9,
        "core_maths": 0.2,
        "integrated_science": 0.5,
        "social_studies": 0.5,
    }
    mix5 = subject_mix_for_level(1, acc)
    mix6 = subject_mix_for_level(6, acc)
    mix10 = subject_mix_for_level(8, acc)
    assert sum(mix5.values()) == 5
    assert sum(mix6.values()) == 6
    assert sum(mix10.values()) == 10
    assert all(v >= 1 for v in mix5.values())


def test_next_adjustment_respects_floor():
    cfg = AdaptiveConfig(low_accuracy=0.5, adj_step=1, difficulty_max=15)
    assert next_adjustment(0, 0.1, phase_floor=1, baseline=1, cfg=cfg) == 0


def test_rolling_accuracy_moves_toward_observation():
    mid = update_rolling_accuracy(0.5, True, window=20)
    assert mid > 0.5
    low = update_rolling_accuracy(0.5, False, window=20)
    assert low < 0.5


def test_weak_streak_and_nudge():
    cfg = AdaptiveConfig(low_accuracy=0.5, learning_nudge_levels=2)
    s1 = update_weak_streak(0, 0.4, cfg)
    assert s1 == 1
    s2 = update_weak_streak(s1, 0.3, cfg)
    assert s2 == 2
    assert should_nudge_learning(s2, cfg) is True
    reset = update_weak_streak(s2, 0.8, cfg)
    assert reset == 0
    assert should_nudge_learning(reset, cfg) is False


def test_adaptive_subject_mix_boosts_weak_subjects():
    base = {"english": 3, "core_maths": 3, "integrated_science": 2, "social_studies": 2}
    mix = adaptive_subject_mix(
        base,
        {
            "english": 0.95,
            "core_maths": 0.2,
            "integrated_science": 0.6,
            "social_studies": 0.6,
        },
    )
    assert sum(mix.values()) == 10
    assert mix["core_maths"] > mix["english"]
    assert all(v >= 1 for v in mix.values())


def test_expand_subject_queue_shuffles_and_preserves_counts():
    mix = {"english": 3, "core_maths": 2}
    rng = random.Random(0)
    queue = expand_subject_queue(mix, rng)
    assert len(queue) == 5
    assert queue.count("english") == 3
    assert queue.count("core_maths") == 2


def test_normalize_question_text():
    assert normalize_question_text("  Hello   World ") == "hello world"
