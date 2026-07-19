"""
prefetch_manager.py
───────────────────
Background prefetch of AI-generated questions via NVIDIA API.

Implements a stale-while-revalidate pattern:
1. Static DB questions are served immediately while AI questions generate.
2. AI questions are prefetched in the background on calibration start.
3. Once ready, they are injected into the next_questions piggyback so
   the frontend sees them seamlessly.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from app.assessment.deepseek_service import generate_challenge_question

logger = logging.getLogger(__name__)

# Difficulty -> IRT difficulty_b mapping
DIFFICULTY_MAP = {
    "Beginner": -1.0,
    "Intermediate": 0.0,
    "Advanced": 1.0,
}

CATEGORY_CYCLE = [
    "Logic",
    "Quantitative Thinking",
    "Scientific Thinking",
    "Verbal Reasoning",
    "Critical Thinking",
]

# Science sub-domain rotation — ensures every science question
# covers a different branch of science with real scientific content.
SCIENCE_CONCEPTS = [
    # Physics
    {"concept": "Newton's laws of motion and friction", "subdomain": "Physics"},
    {"concept": "Ohm's law and electrical circuits", "subdomain": "Physics"},
    {"concept": "Waves — sound, light, and the electromagnetic spectrum", "subdomain": "Physics"},
    {"concept": "Thermodynamics — heat transfer and the laws of energy", "subdomain": "Physics"},
    {"concept": "Optics — reflection, refraction, and lenses", "subdomain": "Physics"},
    # Chemistry
    {"concept": "Atomic structure and the periodic table trends", "subdomain": "Chemistry"},
    {"concept": "Chemical bonding — ionic, covalent, and metallic", "subdomain": "Chemistry"},
    {"concept": "Stoichiometry — mole concept and balancing equations", "subdomain": "Chemistry"},
    {"concept": "Acids, bases, and pH — neutralisation reactions", "subdomain": "Chemistry"},
    {"concept": "Organic chemistry — hydrocarbons and functional groups", "subdomain": "Chemistry"},
    # Biology
    {"concept": "Photosynthesis and cellular respiration", "subdomain": "Biology"},
    {"concept": "DNA structure, replication, and protein synthesis", "subdomain": "Biology"},
    {"concept": "Human circulatory and respiratory systems", "subdomain": "Biology"},
    {"concept": "Genetics — Mendelian inheritance and Punnett squares", "subdomain": "Biology"},
    {"concept": "Ecology — food webs, energy flow, and nutrient cycles", "subdomain": "Biology"},
    # Earth & Space
    {"concept": "Plate tectonics, earthquakes, and volcanic activity", "subdomain": "Earth Science"},
    {"concept": "The rock cycle and types of rocks", "subdomain": "Earth Science"},
    {"concept": "Weather and climate — atmospheric processes", "subdomain": "Earth Science"},
    {"concept": "The solar system — planetary motion and gravity", "subdomain": "Astronomy"},
    {"concept": "Stellar evolution — life cycle of stars", "subdomain": "Astronomy"},
    # Environmental & Health
    {"concept": "Climate change — greenhouse effect and renewable energy", "subdomain": "Environmental Science"},
    {"concept": "Ecosystem conservation and biodiversity loss", "subdomain": "Environmental Science"},
    {"concept": "Human nutrition — macronutrients and deficiencies", "subdomain": "Health Science"},
    {"concept": "Infectious diseases and the immune system", "subdomain": "Health Science"},
]


@dataclass
class PrefetchEntry:
    """Tracks prefetch state for a single user session."""
    questions: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "idle"  # idle | fetching | ready | error
    error: Optional[str] = None
    started_at: Optional[float] = None


class PrefetchManager:
    """In-memory prefetch manager, one entry per user_id."""

    def __init__(self) -> None:
        self._cache: Dict[str, PrefetchEntry] = {}

    # ── Public API ──────────────────────────────────────────────────────────

    def start_prefetch(self, user_id: str, programme: str, count: int = 5) -> None:
        """Fire off a background task to prefetch AI questions."""
        if user_id in self._cache and self._cache[user_id].status == "fetching":
            logger.info(f"Prefetch already in progress for user {user_id}")
            return

        entry = PrefetchEntry(status="fetching", started_at=time.time())
        self._cache[user_id] = entry
        asyncio.create_task(self._do_prefetch(user_id, programme, count))
        logger.info(f"[Prefetch] Started for user={user_id} programme={programme} count={count}")

    def get_questions(self, user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Pull up to `limit` prefetched questions (consumes them)."""
        entry = self._cache.get(user_id)
        if not entry or entry.status != "ready" or not entry.questions:
            return []
        batch = entry.questions[:limit]
        entry.questions = entry.questions[limit:]
        if entry.questions:
            entry.status = "ready"
        else:
            entry.status = "idle"
        return batch

    def has_questions(self, user_id: str) -> bool:
        entry = self._cache.get(user_id)
        return entry is not None and entry.status == "ready" and bool(entry.questions)

    def status(self, user_id: str) -> str:
        entry = self._cache.get(user_id)
        return entry.status if entry else "idle"

    def clear(self, user_id: str) -> None:
        self._cache.pop(user_id, None)

    # ── Background worker ───────────────────────────────────────────────────

    async def _do_prefetch(self, user_id: str, programme: str, count: int) -> None:
        """Fetch `count` questions from NVIDIA API, cycling categories/difficulties.
        
        For Scientific Thinking, rotates through different branches of science
        (physics, chemistry, biology, earth science, astronomy, environmental, health)
        with specific real-world concepts — so every science question is unique.
        """
        generated: List[Dict[str, Any]] = []
        science_idx = 0

        for i in range(count):
            category = CATEGORY_CYCLE[i % len(CATEGORY_CYCLE)]
            difficulty = ["Beginner", "Intermediate", "Advanced"][i % 3]

            concept = None
            if category == "Scientific Thinking" and SCIENCE_CONCEPTS:
                sci = SCIENCE_CONCEPTS[science_idx % len(SCIENCE_CONCEPTS)]
                concept = sci["concept"]
                science_idx += 1

            try:
                result = await generate_challenge_question(
                    category=category,
                    difficulty=difficulty,
                    programme=programme or "General Science",
                    concept=concept,
                )
            except Exception as exc:
                logger.warning(f"[Prefetch] NVIDIA call failed ({exc}) — continuing")
                continue

            if not result.get("success"):
                logger.warning(f"[Prefetch] Generation failed: {result.get('error')}")
                continue

            ai_q = result["data"]
            letters = ["A", "B", "C", "D"]

            # Convert options list → dict {A: ..., B: ..., ...}
            options_dict: Dict[str, str] = {}
            for idx, opt in enumerate(ai_q["options"]):
                if idx < len(letters):
                    options_dict[letters[idx]] = str(opt)

            # Normalise correct_answer to a letter
            answer = ai_q["correct_answer"]
            if answer in letters:
                correct_letter = answer
            elif answer in ai_q["options"]:
                correct_letter = letters[ai_q["options"].index(answer)]
            else:
                correct_letter = "A"

            generated.append({
                "id": -(i + 1),  # Negative IDs = AI-generated (no DB clash)
                "domain": ai_q.get("category", category),
                "question": ai_q["question"],
                "options": options_dict,
                "correct_answer": correct_letter,
                "difficulty_a": 1.2,
                "difficulty_b": DIFFICULTY_MAP.get(ai_q.get("difficulty", "Intermediate"), 0.0),
                "difficulty_c": 0.25,
                "explanation": ai_q.get("explanation", ""),
                "is_ai_generated": True,
            })

        entry = self._cache.get(user_id)
        if not entry:
            return

        if generated:
            entry.questions = generated
            entry.status = "ready"
            elapsed = time.time() - (entry.started_at or time.time())
            logger.info(f"[Prefetch] Done for user={user_id} — {len(generated)} qs in {elapsed:.1f}s")
        else:
            entry.status = "error"
            entry.error = "All AI generation attempts failed"
            logger.warning(f"[Prefetch] All {count} attempts failed for user={user_id}")


# Singleton shared across the app
prefetch_manager = PrefetchManager()
