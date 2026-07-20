"""Adaptive difficulty helpers — unit-testable pure functions."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class AdaptiveConfig:
    rolling_window: int = 20
    low_accuracy: float = 0.50
    high_accuracy: float = 0.85
    adj_step: int = 1
    difficulty_min: int = 1
    difficulty_max: int = 15
    learning_nudge_levels: int = 2


def clamp_difficulty(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def effective_difficulty(
    baseline: int,
    adjustment: int,
    phase_floor: int,
    cfg: AdaptiveConfig,
) -> int:
    """
    effective = baseline + adjustment, clamped to [max(phase_floor, min), max].
    Per-subject easing never drops below the phase Level-1 baseline (phase_floor).
    """
    floor = max(phase_floor, cfg.difficulty_min)
    return clamp_difficulty(baseline + adjustment, floor, cfg.difficulty_max)


def update_rolling_accuracy(
    previous: float,
    is_correct: bool,
    window: int,
) -> float:
    """Simple EMA approximating a windowed average."""
    alpha = 2 / (max(window, 2) + 1)
    observation = 1.0 if is_correct else 0.0
    return previous * (1 - alpha) + observation * alpha


def next_adjustment(
    current_adj: int,
    rolling_accuracy: float,
    phase_floor: int,
    baseline: int,
    cfg: AdaptiveConfig,
) -> int:
    """
    Raise difficulty only when the learner is strong in this subject.
    Weak subjects keep the same difficulty (never eased downward) so ML still
    sees a stable signal and the next level does not get easier by default.
    """
    adj = current_adj
    if rolling_accuracy > cfg.high_accuracy:
        adj += cfg.adj_step

    min_adj = phase_floor - baseline
    max_adj = cfg.difficulty_max - baseline
    return max(min_adj, min(max_adj, adj))


def bump_adjustment_if_strong(
    current_adj: int,
    session_accuracy: float,
    phase_floor: int,
    baseline: int,
    cfg: AdaptiveConfig,
    *,
    strong_threshold: float = 0.5,
) -> int:
    """After a level: subjects answered mostly correctly step up once."""
    adj = current_adj
    if session_accuracy >= strong_threshold:
        adj += cfg.adj_step
    min_adj = phase_floor - baseline
    max_adj = cfg.difficulty_max - baseline
    return max(min_adj, min(max_adj, adj))


def level_question_count(level_number: int) -> int:
    """
    How many challenge questions appear at this phase level.
    L1–5 → 5, L6–7 → 6, L8–10 → 10.
    """
    n = int(level_number or 1)
    if n <= 5:
        return 5
    if n <= 7:
        return 6
    return 10


def subject_mix_for_level(
    level_number: int,
    accuracies: dict[str, float],
    subject_keys: list[str] | None = None,
) -> dict[str, int]:
    """
    Build a per-level subject mix totaling level_question_count(...).
    Still tilts slightly toward weaker subjects without dropping the total.
    """
    keys = subject_keys or [
        "english",
        "core_maths",
        "integrated_science",
        "social_studies",
    ]
    total = level_question_count(level_number)
    if total <= 0:
        return {s: 0 for s in keys}

    # Even base distribution, then adapt toward weaknesses.
    base = {s: 0 for s in keys}
    for i, s in enumerate(keys):
        base[s] = total // len(keys) + (1 if i < total % len(keys) else 0)
    return adaptive_subject_mix(base, accuracies)


def update_weak_streak(previous_streak: int, rolling_accuracy: float, cfg: AdaptiveConfig) -> int:
    if rolling_accuracy < cfg.low_accuracy:
        return previous_streak + 1
    return 0


def should_nudge_learning(weak_streak: int, cfg: AdaptiveConfig) -> bool:
    return weak_streak >= cfg.learning_nudge_levels


def adaptive_subject_mix(
    base_mix: dict[str, int],
    accuracies: dict[str, float],
) -> dict[str, int]:
    """
    Redistribute the same total question count toward weaker subjects.

    Lower rolling accuracy → slightly more questions next level.
    Every subject in base_mix keeps at least 1 if total >= number of subjects.
    """
    if not base_mix:
        return {}
    total = sum(base_mix.values())
    subjects = list(base_mix.keys())
    if total <= 0:
        return {s: 0 for s in subjects}

    weights: dict[str, float] = {}
    for s in subjects:
        acc = accuracies.get(s)
        if acc is None:
            acc = 0.5
        # Weak subjects get higher weight; floor so strong subjects still appear
        weights[s] = max(0.2, 1.0 - float(acc))

    wsum = sum(weights.values()) or 1.0
    # Largest-remainder allocation
    exact = {s: total * weights[s] / wsum for s in subjects}
    floored = {s: int(exact[s]) for s in subjects}
    # Ensure minimum 1 when possible
    if total >= len(subjects):
        for s in subjects:
            if floored[s] < 1:
                floored[s] = 1
        while sum(floored.values()) > total:
            # Trim from strongest (highest accuracy / lowest weight)
            strongest = max(subjects, key=lambda x: (floored[x] > 1, accuracies.get(x, 0.5), -weights[x]))
            if floored[strongest] > 1:
                floored[strongest] -= 1
            else:
                break

    remainder = total - sum(floored.values())
    order = sorted(subjects, key=lambda s: (exact[s] - floored[s]), reverse=True)
    i = 0
    while remainder > 0 and subjects:
        floored[order[i % len(order)]] += 1
        remainder -= 1
        i += 1
    return floored


def expand_subject_queue(mix: dict[str, int], rng) -> list[str]:
    """Expand counts into a shuffled subject list (random order within the level)."""
    queue: list[str] = []
    for subject, count in mix.items():
        queue.extend([subject] * max(0, int(count)))
    rng.shuffle(queue)
    return queue


def normalize_question_text(text: str) -> str:
    """Normalize for within-level duplicate detection."""
    cleaned = re.sub(r"\s+", " ", (text or "").strip().lower())
    return cleaned
