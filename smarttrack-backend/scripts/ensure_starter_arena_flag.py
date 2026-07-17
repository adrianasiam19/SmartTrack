"""Ensure starter_arena_completed exists and backfill completed users."""
from __future__ import annotations

import asyncio
import selectors
import sys


def _run(coro):
    if sys.platform == "win32":
        return asyncio.run(
            coro,
            loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
        )
    return asyncio.run(coro)


async def main() -> None:
    from sqlalchemy import text

    from app.database import engine

    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS starter_arena_completed BOOLEAN
                NOT NULL DEFAULT false
                """
            )
        )
        result = await conn.execute(
            text(
                """
                UPDATE users
                SET starter_arena_completed = true
                WHERE onboarding_completed = true
                  AND starter_arena_completed = false
                """
            )
        )
        print(f"Backfilled starter_arena_completed for {result.rowcount} users.")

    await engine.dispose()


if __name__ == "__main__":
    _run(main())
