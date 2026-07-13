"""
run.py — Atlas API entry point for Windows compatibility.
Sets the event loop policy before uvicorn creates the loop,
preventing Psycopg's ProactorEventLoop error on Windows.
"""
import asyncio
import sys

# ── Windows event-loop fix ────────────────────────────────────────────────
# Psycopg 3 (async) cannot use ProactorEventLoop (the default on Windows).
# We must set the policy BEFORE uvicorn creates the event loop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
