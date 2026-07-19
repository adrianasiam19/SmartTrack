"""
Seed 3 phases × 10 levels.
Usage: python -m scripts.seed_phases_levels
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.phases.models import Level, Phase

PHASES = [
    (1, "Phase 1", "Build foundations across core subjects.", "SHS 1"),
    (2, "Phase 2", "Strengthen skills and explore deeper challenges.", "SHS 2"),
    (3, "Phase 3", "Consolidate mastery and prepare for your path.", "SHS 3"),
]


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        await db.execute(delete(Level))
        await db.execute(delete(Phase))
        await db.commit()

        for number, name, description, shs in PHASES:
            phase = Phase(
                number=number,
                name=name,
                description=description,
                shs_mapping=shs,
            )
            db.add(phase)
            await db.flush()
            for lvl in range(1, 11):
                db.add(
                    Level(
                        phase_id=phase.id,
                        number=lvl,
                        difficulty_baseline=lvl,
                    )
                )
        await db.commit()
        phases = (await db.execute(select(Phase))).scalars().all()
        levels = (await db.execute(select(Level))).scalars().all()
        print(f"Seeded {len(phases)} phases, {len(levels)} levels")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
