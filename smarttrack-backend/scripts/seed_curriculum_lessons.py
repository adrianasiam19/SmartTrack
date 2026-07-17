"""Upsert exported SHS 1/2 curriculum lessons into PostgreSQL."""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

from sqlalchemy.dialects.postgresql import insert

from app.assessment.models import CurriculumLesson
from app.database import AsyncSessionLocal, engine

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "curriculum_lessons.json"
ALLOWED_LEVELS = {"SHS 1", "SHS 2"}


def _collect_strings(value: Any, output: list[str]) -> None:
    if isinstance(value, str):
        output.append(value)
    elif isinstance(value, list):
        for item in value:
            _collect_strings(item, output)
    elif isinstance(value, dict):
        for item in value.values():
            _collect_strings(item, output)


def _search_text(record: dict[str, Any]) -> str:
    values: list[str] = [record["title"], record["subject"]]
    _collect_strings(record["source_content"], values)
    return re.sub(r"\s+", " ", " ".join(values)).strip().lower()


async def seed() -> None:
    records = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        raise RuntimeError("Curriculum export is empty or invalid")

    values = []
    for record in records:
        levels = record.get("shs_levels", [])
        if not levels or any(level not in ALLOWED_LEVELS for level in levels):
            raise RuntimeError(
                f"Invalid SHS level in curriculum lesson {record.get('curriculum_id')}"
            )
        values.append(
            {
                **record,
                "search_text": _search_text(record),
                "ai_content_by_level": {},
                "ai_content_version": "v1",
            }
        )

    # Development databases may use create_all before Alembic is brought up to date.
    # checkfirst keeps this safe while the committed migration remains authoritative.
    async with engine.begin() as connection:
        await connection.run_sync(
            lambda sync_connection: CurriculumLesson.__table__.create(
                sync_connection, checkfirst=True
            )
        )

    async with AsyncSessionLocal() as session:
        for start in range(0, len(values), 50):
            statement = insert(CurriculumLesson).values(values[start : start + 50])
            excluded = statement.excluded
            statement = statement.on_conflict_do_update(
                index_elements=[CurriculumLesson.curriculum_id],
                set_={
                    "title": excluded.title,
                    "subject": excluded.subject,
                    "programme": excluded.programme,
                    "shs_levels": excluded.shs_levels,
                    "unit_id": excluded.unit_id,
                    "difficulty": excluded.difficulty,
                    "estimated_minutes": excluded.estimated_minutes,
                    "xp_reward": excluded.xp_reward,
                    "source_content": excluded.source_content,
                    "search_text": excluded.search_text,
                },
            )
            await session.execute(statement)
        await session.commit()

    print(f"Seeded {len(values)} SHS 1/2 curriculum lessons.")
    await engine.dispose()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed())
