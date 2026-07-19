"""
psychometric_cards.py
─────────────────────
Psychometric Insight Cards for the Atlas Challenge Arena.

Cards are loaded from data/psychometric_cards.json (400 questions
across 20 categories). The database is the canonical source; this
module serves as a fallback when the DB is empty.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

# ── Type ─────────────────────────────────────────────────────────────────────
PsychometricCard = Dict[str, Any]

# ── Load cards from JSON data file ───────────────────────────────────────────
_json_path = Path(__file__).resolve().parent.parent.parent / "data" / "psychometric_cards.json"

if _json_path.exists():
    with open(_json_path, "r", encoding="utf-8") as _f:
        PSYCHOMETRIC_CARDS: List[PsychometricCard] = json.load(_f)
else:
    PSYCHOMETRIC_CARDS: List[PsychometricCard] = []


def get_psychometric_card(card_id: str) -> PsychometricCard | None:
    """Look up a specific psychometric card by ID."""
    for card in PSYCHOMETRIC_CARDS:
        if card["id"] == card_id:
            return card
    return None


def get_cards_by_category(category: str) -> List[PsychometricCard]:
    """Get all cards for a specific trait category."""
    return [c for c in PSYCHOMETRIC_CARDS if c["category"] == category]


def pick_cards_for_session(count: int = 3,
                            exclude_ids: List[str] | None = None,
                            preferred_categories: List[str] | None = None) -> List[PsychometricCard]:
    """
    Pick a balanced set of psychometric cards for a challenge session.

    Args:
      count: Number of cards to pick.
      exclude_ids: Card IDs to exclude (already shown).
      preferred_categories: If set, prioritise these categories.

    Returns:
      A list of PsychometricCard objects.
    """
    import random
    pool = [c for c in PSYCHOMETRIC_CARDS if not exclude_ids or c["id"] not in exclude_ids]

    if preferred_categories and pool:
        preferred = [c for c in pool if c["category"] in preferred_categories]
        if preferred:
            chosen = [random.choice(preferred)]
            pool = [c for c in pool if c["id"] != chosen[0]["id"]]
            count -= 1
            if count > 0:
                chosen.extend(random.sample(pool, min(count, len(pool))))
            return chosen

    selected = random.sample(pool, min(count, len(pool)))
    return selected


def get_categories() -> List[str]:
    """Get all available psychometric card categories."""
    return list(set(c["category"] for c in PSYCHOMETRIC_CARDS))


# ── Flatten for API responses ────────────────────────────────────────────────
def flatten_card_for_api(card: PsychometricCard) -> Dict:
    """Remove trait_weights from options for frontend consumption."""
    return {
        "id": card["id"],
        "category": card["category"],
        "question": card["question"],
        "display": card["display"],
        "options": [
            {"value": o["value"], "label": o["label"]}
            for o in card["options"]
        ],
    }
