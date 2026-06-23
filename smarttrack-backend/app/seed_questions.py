"""
Seed script for the Atlas Challenge Arena question bank.
Run with: python -m app.seed_questions

Uses questions_v2.json (generated from question templates) which includes
arena, difficulty_tier, explanation, template_id, and IRT parameters.
Also seeds psychometric insight cards from the psychometric_cards module.
"""
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import json
import os
from typing import List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete
from app.assessment.models import Question, LearningModule, PsychometricCard
from app.assessment.psychometric_cards import PSYCHOMETRIC_CARDS
from app.config import settings

# ── Data directory ─────────────────────────────────────────────────────────────
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load_json(filename: str) -> list:
    path = os.path.join(_DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_questions():
    """Insert challenge questions, learning modules, and psychometric cards."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # ── 1. Seed Questions (from questions_v2.json) ────────────────────────
        await session.execute(delete(Question))
        await session.commit()

        try:
            raw: List[dict] = _load_json("questions_v2.json")
            to_insert = []
            for i, q in enumerate(raw, start=1):
                to_insert.append(Question(
                    id=i,
                    domain=q.get("domain", "General"),
                    arena=q.get("arena"),
                    difficulty_tier=q.get("difficulty_tier"),
                    shs_levels=q.get("shs_levels"),
                    template_id=q.get("template_id"),
                    question=q["question"],
                    options=q["options"],
                    correct_answer=q["correct_answer"],
                    explanation=q.get("explanation"),
                    difficulty_a=q.get("difficulty_a", 1.0),
                    difficulty_b=q.get("difficulty_b", 0.0),
                    difficulty_c=q.get("difficulty_c", 0.25),
                ))
            print(f"[INFO] Loaded {len(to_insert)} questions from data/questions_v2.json")
        except Exception as e:
            print(f"[WARN] Could not load questions_v2.json ({e}).")
            print(f"[WARN] Attempting fallback to questions.json...")
            try:
                raw = _load_json("questions.json")
                to_insert = []
                for i, q in enumerate(raw, start=1):
                    to_insert.append(Question(
                        id=i,
                        domain=q.get("domain", "General"),
                        question=q["question"],
                        options=q["options"],
                        correct_answer=q["correct_answer"],
                        explanation=q.get("explanation"),
                        difficulty_a=q.get("difficulty_a", 1.0),
                        difficulty_b=q.get("difficulty_b", 0.0),
                        difficulty_c=q.get("difficulty_c", 0.25),
                    ))
                print(f"[INFO] Loaded {len(to_insert)} questions from data/questions.json (fallback)")
            except Exception as e2:
                print(f"[ERROR] Both files failed: {e2}")
                return

        for q in to_insert:
            session.add(q)
        await session.commit()
        print(f"[OK] Seeded {len(to_insert)} challenge questions.")

        # ── 2. Seed Learning Modules ───────────────────────────────────────────
        await session.execute(delete(LearningModule))
        await session.commit()

        try:
            mods = _load_json("modules.json")
            for i, m in enumerate(mods, start=1):
                session.add(LearningModule(
                    id=i,
                    domain=m["domain"],
                    title=m["title"],
                    content=m["content"],
                    difficulty_level=m.get("difficulty_level", 0.0),
                ))
            await session.commit()
            print(f"[OK] Seeded {len(mods)} learning modules.")
        except Exception as e:
            print(f"[WARN] Could not seed learning modules: {e}")

        # ── 3. Seed Psychometric Cards ─────────────────────────────────────────
        await session.execute(delete(PsychometricCard))
        await session.commit()

        if PSYCHOMETRIC_CARDS:
            for i, card in enumerate(PSYCHOMETRIC_CARDS, start=1):
                session.add(PsychometricCard(
                    id=i,
                    card_id=card["id"],
                    question=card["question"],
                    options=card.get("options", []),
                    trait_mapping=card.get("trait_mapping"),
                ))
            await session.commit()
            print(f"[OK] Seeded {len(PSYCHOMETRIC_CARDS)} psychometric cards.")
        else:
            print("[WARN] No psychometric cards to seed.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_questions())
