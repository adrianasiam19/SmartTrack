"""Unit tests for adaptive difficulty clamps / EMA / nudge."""
from app.phases.adaptive import (
    AdaptiveConfig,
    adaptive_subject_mix,
    effective_difficulty,
    expand_subject_queue,
    next_adjustment,
    normalize_question_text,
    should_nudge_learning,
    update_rolling_accuracy,
    update_weak_streak,
)
import random


def test_effective_difficulty_respects_phase_floor():
    cfg = AdaptiveConfig(difficulty_min=1, difficulty_max=15)
    # baseline 5, big negative adj → floor at phase L1 baseline (1)
    assert effective_difficulty(5, -10, phase_floor=1, cfg=cfg) == 1
    # phase floor 3
    assert effective_difficulty(5, -10, phase_floor=3, cfg=cfg) == 3


def test_effective_difficulty_clamps_max():
    cfg = AdaptiveConfig(difficulty_min=1, difficulty_max=15)
    assert effective_difficulty(10, 20, phase_floor=1, cfg=cfg) == 15


def test_next_adjustment_decreases_on_low_accuracy():
    cfg = AdaptiveConfig(low_accuracy=0.5, high_accuracy=0.85, adj_step=1)
    assert next_adjustment(0, 0.4, phase_floor=1, baseline=5, cfg=cfg) == -1


def test_next_adjustment_increases_on_high_accuracy():
    cfg = AdaptiveConfig(low_accuracy=0.5, high_accuracy=0.85, adj_step=1)
    assert next_adjustment(0, 0.9, phase_floor=1, baseline=5, cfg=cfg) == 1


def test_next_adjustment_respects_floor():
    cfg = AdaptiveConfig(low_accuracy=0.5, adj_step=1, difficulty_max=15)
    # baseline 1, cannot go below floor 1 → min_adj = 0
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
    # maths very weak, english strong
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
