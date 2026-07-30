"""Deterministic soft scoring for KNUST programmes (teacher for DT labels)."""
from __future__ import annotations

from typing import Any


def family_soft_fit(
    family: str,
    *,
    pts: dict[str, float],
    traits: dict[str, float],
    accuracies: dict[str, float],
) -> float:
    """
    Higher is better. Uses inverted WAEC points (1 best → strength 8, 9 worst → 0)
    plus psychometric / arena signals.
    """

    def strength(key: str) -> float:
        p = float(pts.get(key, 9.0))
        return max(0.0, 9.0 - p)

    analytical = float(traits.get("analytical", 50)) / 100.0
    empathy = float(traits.get("empathy", 50)) / 100.0
    practical = float(traits.get("practical", 50)) / 100.0
    creative = float(traits.get("creative", 50)) / 100.0
    science_acc = float(accuracies.get("scientific", 50)) / 100.0
    quant_acc = float(accuracies.get("quant", 50)) / 100.0
    logic_acc = float(accuracies.get("logic", 50)) / 100.0

    f = family.strip()
    if f == "Health Sciences":
        return (
            strength("biology") * 3.0
            + strength("chemistry") * 2.5
            + strength("physics") * 1.0
            + empathy * 25.0
            + science_acc * 15.0
            + analytical * 8.0
        )
    if f == "Engineering":
        return (
            strength("elective_maths") * 3.0
            + strength("physics") * 2.5
            + strength("core_maths") * 2.0
            + strength("chemistry") * 1.0
            + practical * 20.0
            + analytical * 15.0
            + quant_acc * 12.0
            + logic_acc * 8.0
        )
    # Science (Natural Sciences catalogue family)
    return (
        strength("biology") * 1.5
        + strength("chemistry") * 1.5
        + strength("physics") * 1.5
        + strength("elective_maths") * 2.0
        + strength("core_maths") * 1.5
        + strength("integrated_science") * 1.0
        + analytical * 12.0
        + creative * 8.0
        + science_acc * 12.0
        + quant_acc * 10.0
    )


def programme_soft_score(
    row: dict[str, Any],
    *,
    aggregate: int,
    pts: dict[str, float],
    traits: dict[str, float],
    accuracies: dict[str, float],
) -> float:
    """Score one KNUST catalogue row for label selection (higher = better teacher pick)."""
    family = str(row.get("family") or "")
    cutoff = int(row.get("cutoff") or 99)
    fit = family_soft_fit(family, pts=pts, traits=traits, accuracies=accuracies)
    headroom = cutoff - int(aggregate)
    # Profile fit dominates. Prefer more competitive (lower cutoff) programmes you still clear.
    # Small headroom term — do NOT reward the easiest programmes.
    return fit * 12.0 - float(cutoff) * 1.25 + min(headroom, 4) * 0.15
