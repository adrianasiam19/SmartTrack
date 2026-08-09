"""Smoke-test Stage 7 engine against local DB."""
from __future__ import annotations

import asyncio
import selectors

from sqlalchemy import select, text

from app.database import AsyncSessionLocal
from app.notifications.engine import run_notification_engine
from app.notifications.models import Notification
from app.users.models import User


async def main() -> None:
    async with AsyncSessionLocal() as db:
        user = (
            await db.execute(
                select(User).where(User.id == "4502904b-44e6-4abe-949e-edb4a4ef9acb")
            )
        ).scalar_one_or_none()
        if not user:
            user = (await db.execute(select(User).limit(1))).scalar_one()
        print("user", user.email, "streak", user.streak, "rank", user.rank)
        profile = user.learner_profile if isinstance(user.learner_profile, dict) else {}
        print("engine_last_run", profile.get("notif_engine_last_run"))
        result = await run_notification_engine(db, user, force=True)
        print("engine_result", result)
        rows = (
            await db.execute(
                select(Notification)
                .where(Notification.user_id == user.id)
                .order_by(Notification.created_at.desc())
                .limit(8)
            )
        ).scalars().all()
        for n in rows:
            data = n.data or {}
            print(
                "-",
                n.created_at,
                n.category,
                n.title,
                "|",
                (n.message or "")[:70],
                "| rule=",
                data.get("rule_key"),
            )


if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
    )
