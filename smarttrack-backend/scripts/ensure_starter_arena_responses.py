"""
Ensure Starter Arena persistence columns/tables exist.

Useful when Alembic revision history is out of sync with Neon.
"""
from __future__ import annotations

import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


SQL_STATEMENTS = [
    """
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS learner_profile JSON
    """,
    """
    CREATE TABLE IF NOT EXISTS starter_arena_responses (
        id SERIAL PRIMARY KEY,
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        session_id VARCHAR(120) NOT NULL,
        question_id VARCHAR(120) NOT NULL,
        question_text TEXT NOT NULL,
        question_type VARCHAR(30) NOT NULL,
        source VARCHAR(20) NOT NULL,
        category VARCHAR(100),
        cognitive_skill VARCHAR(100),
        question_format VARCHAR(40) NOT NULL,
        options JSON NOT NULL,
        answer TEXT NOT NULL,
        correct BOOLEAN,
        time_taken_seconds DOUBLE PRECISION NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CONSTRAINT uq_starter_response_user_session_question
            UNIQUE (user_id, session_id, question_id)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_starter_arena_responses_id
    ON starter_arena_responses (id)
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_starter_arena_responses_user_id
    ON starter_arena_responses (user_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_starter_arena_responses_session_id
    ON starter_arena_responses (session_id)
    """,
]


async def main() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        for statement in SQL_STATEMENTS:
            await conn.execute(text(statement))
    await engine.dispose()
    print("Ensured users.learner_profile and starter_arena_responses exist.")


if __name__ == "__main__":
    asyncio.run(main())
