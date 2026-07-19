"""Heuristic tagging for Get-to-Know-You options + review queue."""
from __future__ import annotations

from typing import Any

PROGRAMME_TYPES = (
    "engineering",
    "technology",
    "medicine_health",
    "business_law",
    "arts_media",
    "natural_sciences",
    "social_sciences",
    "environment",
    "research_academia",
)

# Learning Preferences labels A–D map cleanly to VARK-style traits
LEARNING_PREF_TRAITS = {
    "A": ["visual"],
    "B": ["auditory"],
    "C": ["reading_writing"],
    "D": ["kinesthetic"],
}

CATEGORY_PROGRAMME_HINTS: dict[str, list[dict[str, Any]]] = {
    "Technology Interest": [
        {"programme": "technology", "weight": 0.8},
        {"programme": "engineering", "weight": 0.5},
    ],
    "Engineering Interest": [
        {"programme": "engineering", "weight": 0.9},
        {"programme": "technology", "weight": 0.4},
    ],
    "Medical and Health Interest": [
        {"programme": "medicine_health", "weight": 0.9},
        {"programme": "natural_sciences", "weight": 0.4},
    ],
    "Environmental Interest": [
        {"programme": "environment", "weight": 0.9},
        {"programme": "natural_sciences", "weight": 0.5},
    ],
    "Research Interest": [
        {"programme": "research_academia", "weight": 0.9},
        {"programme": "natural_sciences", "weight": 0.4},
    ],
    "Career Interests": [],  # option-specific below
    "Academic Interests": [],
    "Creativity": [{"programme": "arts_media", "weight": 0.5}],
    "Leadership": [{"programme": "business_law", "weight": 0.4}],
    "Communication": [{"programme": "arts_media", "weight": 0.35}],
}

CAREER_OPTION_AFFINITY = {
    "A": [
        {"programme": "engineering", "weight": 0.7},
        {"programme": "technology", "weight": 0.6},
        {"programme": "natural_sciences", "weight": 0.5},
    ],
    "B": [{"programme": "medicine_health", "weight": 0.8}, {"programme": "social_sciences", "weight": 0.4}],
    "C": [{"programme": "arts_media", "weight": 0.8}],
    "D": [{"programme": "business_law", "weight": 0.8}],
}

ACADEMIC_OPTION_AFFINITY = {
    "A": [{"programme": "natural_sciences", "weight": 0.5}, {"programme": "engineering", "weight": 0.4}],
    "B": [{"programme": "natural_sciences", "weight": 0.7}, {"programme": "medicine_health", "weight": 0.5}],
    "C": [{"programme": "arts_media", "weight": 0.7}, {"programme": "social_sciences", "weight": 0.4}],
    "D": [{"programme": "business_law", "weight": 0.7}, {"programme": "social_sciences", "weight": 0.5}],
}

TRAIT_BY_CATEGORY_DEFAULT = {
    "Curiosity": "curiosity",
    "Creativity": "creativity",
    "Leadership": "leadership",
    "Teamwork": "teamwork",
    "Persistence": "persistence",
    "Motivation": "motivation",
    "Decision Making": "decision_making",
    "Communication": "communication",
    "Time Management": "time_management",
    "Confidence": "confidence",
    "Study Habits": "study_habits",
    "Problem-Solving Style": "problem_solving",
}


def tag_option(category: str, label: str, option_text: str) -> tuple[list[str] | None, list[dict] | None, bool]:
    """
    Returns (trait_tags, programme_affinity_tags, needs_review).
    needs_review=True when heuristics are weak.
    """
    label = label.upper()
    traits: list[str] = []
    affinity: list[dict] = []
    needs_review = False

    if category == "Learning Preferences":
        traits = list(LEARNING_PREF_TRAITS.get(label, []))
        return traits, None, False

    if category in TRAIT_BY_CATEGORY_DEFAULT:
        traits = [TRAIT_BY_CATEGORY_DEFAULT[category]]
        # Intensity by option: A strongest engagement for interest-like categories
        intensity = {"A": "high", "B": "medium_high", "C": "medium", "D": "low"}.get(label, "medium")
        traits.append(f"{TRAIT_BY_CATEGORY_DEFAULT[category]}:{intensity}")

    if category == "Career Interests":
        affinity = list(CAREER_OPTION_AFFINITY.get(label, []))
        return traits or ["career_interest"], affinity, False

    if category == "Academic Interests":
        affinity = list(ACADEMIC_OPTION_AFFINITY.get(label, []))
        return traits or ["academic_interest"], affinity, False

    hints = CATEGORY_PROGRAMME_HINTS.get(category)
    if hints is not None:
        if hints:
            # Scale weight by option engagement (A strongest interest signal)
            scale = {"A": 1.0, "B": 0.7, "C": 0.4, "D": 0.15}.get(label, 0.5)
            affinity = [
                {"programme": h["programme"], "weight": round(h["weight"] * scale, 3)}
                for h in hints
            ]
        else:
            needs_review = True
    else:
        needs_review = True

    if not traits and not affinity:
        needs_review = True
        return None, None, True

    return (traits or None), (affinity or None), needs_review
