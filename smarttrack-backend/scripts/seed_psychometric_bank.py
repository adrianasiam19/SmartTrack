"""
Seed Get-to-Know-You bank + apply heuristic tags.
Usage: python -m scripts.seed_psychometric_bank
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.psychometrics.models import PsychometricOption, PsychometricQuestion
from app.psychometrics.tagging import tag_option

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "atlas_question_bank.json"
REVIEW_PATH = Path(__file__).resolve().parent.parent / "data" / "psychometric_tag_review_queue.json"


async def seed() -> None:
    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    questions = payload["questions"]
    print(f"Loaded {len(questions)} questions")

    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    review_queue: list[dict] = []

    async with Session() as db:
        await db.execute(delete(PsychometricOption))
        await db.execute(delete(PsychometricQuestion))
        await db.commit()

        for q in questions:
            row = PsychometricQuestion(
                bank_id=q["id"],
                number=q["number"],
                category=q["category"],
                text=q["text"],
            )
            db.add(row)
            await db.flush()
            for opt in q["options"]:
                traits, affinity, needs_review = tag_option(
                    q["category"], opt["label"], opt["text"]
                )
                if needs_review:
                    review_queue.append(
                        {
                            "bank_id": q["id"],
                            "number": q["number"],
                            "category": q["category"],
                            "label": opt["label"],
                            "text": opt["text"],
                            "reason": "ambiguous_or_weak_heuristic",
                        }
                    )
                db.add(
                    PsychometricOption(
                        question_id=row.id,
                        label=opt["label"],
                        text=opt["text"],
                        trait_tags=traits,
                        programme_affinity_tags=affinity,
                    )
                )
        await db.commit()

        count = (
            await db.execute(select(PsychometricQuestion))
        ).scalars().all()
        print(f"Seeded {len(count)} questions")

    REVIEW_PATH.write_text(
        json.dumps({"count": len(review_queue), "items": review_queue}, indent=2),
        encoding="utf-8",
    )
    print(f"Review queue: {len(review_queue)} -> {REVIEW_PATH}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
