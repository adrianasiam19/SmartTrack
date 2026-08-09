"""One-off Stage 6 column ensure for local Postgres."""
from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.database import engine


async def migrate() -> None:
    stmts = [
        "ALTER TABLE notifications ADD COLUMN IF NOT EXISTS category VARCHAR(40)",
        "ALTER TABLE notifications ADD COLUMN IF NOT EXISTS action_link VARCHAR(500)",
        "ALTER TABLE notifications ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 1 NOT NULL",
        "UPDATE notifications SET category = type WHERE category IS NULL",
        "UPDATE notifications SET action_link = data->>'href' WHERE action_link IS NULL AND data IS NOT NULL",
        "ALTER TABLE notifications ALTER COLUMN category SET NOT NULL",
    ]
    async with engine.begin() as conn:
        for stmt in stmts:
            try:
                await conn.execute(text(stmt))
                print("ok:", stmt[:70])
            except Exception as exc:
                print("skip/err:", stmt[:50], "->", exc)


if __name__ == "__main__":
    import selectors

    asyncio.run(
        migrate(),
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
    )
    from app.notifications.models import Notification
    from app.notifications.types import MONITORED_SIGNALS

    print("columns:", [c.name for c in Notification.__table__.columns])
    print("signals:", list(MONITORED_SIGNALS))
