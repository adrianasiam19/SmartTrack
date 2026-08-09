"""Rolling background prefetch buffer for phase challenge levels.

Stage 4 architecture:
  - Maintain a modest per-learner buffer of the next ~2–3 levels (not hundreds).
  - Generate full validated question sets (incl. images) in the background.
  - Reuse ready sets until claimed, expired, or format_version changes.
  - start_level claims a ready set when possible; otherwise generates live.

While a learner plays level N, Atlas tops up N+1 … N+buffer in the background.
Dashboard / challenges map can warm the buffer before Start is clicked.
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PrefetchEntry:
    status: str = "idle"  # idle | fetching | ready | error
    level_id: int = 0
    format_version: int = 0
    questions: list[dict[str, Any]] = field(default_factory=list)
    mix: dict[str, int] = field(default_factory=dict)
    phase_number: int = 0
    level_number: int = 0
    error: str | None = None
    started_at: float = 0.0
    ready_at: float | None = None
    retried: bool = False


class PhasePrefetchManager:
    """Per-user rolling cache keyed by level_id (multiple levels at once)."""

    def __init__(self) -> None:
        # key = "{user_id}:{level_id}"
        self._cache: dict[str, PrefetchEntry] = {}
        self._lock = asyncio.Lock()
        # Serialize builds per user so buffer levels share exclude stems.
        self._user_build_locks: dict[str, asyncio.Lock] = {}

    def _entry_key(self, user_id: uuid.UUID, level_id: int) -> str:
        return f"{user_id}:{level_id}"

    def _user_build_lock(self, user_id: uuid.UUID) -> asyncio.Lock:
        key = str(user_id)
        lock = self._user_build_locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._user_build_locks[key] = lock
        return lock

    def _buffer_size(self) -> int:
        return max(1, int(getattr(settings, "CHALLENGE_PREFETCH_BUFFER_LEVELS", 3)))

    def _ttl(self) -> float:
        return float(getattr(settings, "CHALLENGE_PREFETCH_TTL_SECONDS", 900))

    def _current_format(self) -> int:
        return int(getattr(settings, "CHALLENGE_FORMAT_VERSION", 11))

    def _stale(self, entry: PrefetchEntry) -> bool:
        if entry.format_version != self._current_format():
            return True
        if entry.status != "ready" or entry.ready_at is None:
            return False
        return (time.time() - entry.ready_at) > self._ttl()

    def _user_entries(
        self, user_id: uuid.UUID
    ) -> list[tuple[str, PrefetchEntry]]:
        prefix = f"{user_id}:"
        return [(k, e) for k, e in self._cache.items() if k.startswith(prefix)]

    def _prune_user(self, user_id: uuid.UUID, *, protect_level_id: int | None = None) -> None:
        """Drop stale entries; cap ready+fetching slots to buffer size."""
        for key, entry in list(self._user_entries(user_id)):
            if self._stale(entry) and entry.status != "fetching":
                self._cache.pop(key, None)

        live = [
            (k, e)
            for k, e in self._user_entries(user_id)
            if e.status in ("ready", "fetching")
        ]
        limit = self._buffer_size()
        if len(live) <= limit:
            return

        def _age(item: tuple[str, PrefetchEntry]) -> float:
            _k, e = item
            return float(e.ready_at or e.started_at or 0.0)

        # Prefer dropping oldest *ready* first; never drop protect / fetching unless needed.
        ready = sorted(
            [(k, e) for k, e in live if e.status == "ready"],
            key=_age,
        )
        overflow = len(live) - limit
        for key, entry in ready:
            if overflow <= 0:
                break
            if protect_level_id is not None and entry.level_id == protect_level_id:
                continue
            self._cache.pop(key, None)
            overflow -= 1

    def _status_payload(
        self,
        entry: PrefetchEntry | None,
        *,
        level_id: int | None = None,
    ) -> dict[str, Any]:
        if not entry:
            return {"status": "idle", "level_id": level_id, "question_count": 0}
        return {
            "status": entry.status,
            "level_id": entry.level_id,
            "format_version": entry.format_version,
            "question_count": len(entry.questions) if entry.status == "ready" else 0,
            "error": entry.error,
        }

    async def status(
        self, user_id: uuid.UUID, level_id: int | None = None
    ) -> dict[str, Any]:
        if level_id is None:
            return await self.buffer_status(user_id)
        key = self._entry_key(user_id, level_id)
        entry = self._cache.get(key)
        if not entry:
            return self._status_payload(None, level_id=level_id)
        if self._stale(entry):
            if entry.status != "fetching":
                self._cache.pop(key, None)
            return self._status_payload(None, level_id=level_id)
        return self._status_payload(entry, level_id=level_id)

    async def buffer_status(self, user_id: uuid.UUID) -> dict[str, Any]:
        self._prune_user(user_id)
        ready_levels: list[int] = []
        fetching_levels: list[int] = []
        error_levels: list[int] = []
        question_count = 0
        entries: list[dict[str, Any]] = []
        for _key, entry in sorted(
            self._user_entries(user_id), key=lambda kv: kv[1].level_id
        ):
            if self._stale(entry) and entry.status != "fetching":
                continue
            payload = self._status_payload(entry)
            entries.append(payload)
            if entry.status == "ready":
                ready_levels.append(entry.level_id)
                question_count += len(entry.questions)
            elif entry.status == "fetching":
                fetching_levels.append(entry.level_id)
            elif entry.status == "error":
                error_levels.append(entry.level_id)

        if fetching_levels:
            overall = "fetching"
        elif ready_levels:
            overall = "ready"
        elif error_levels:
            overall = "error"
        else:
            overall = "idle"

        return {
            "status": overall,
            "level_id": ready_levels[0] if ready_levels else None,
            "ready_levels": ready_levels,
            "fetching_levels": fetching_levels,
            "error_levels": error_levels,
            "question_count": question_count,
            "buffer_size": self._buffer_size(),
            "buffer": entries,
            "format_version": self._current_format(),
        }

    async def start(
        self,
        user_id: uuid.UUID,
        level_id: int,
        *,
        force: bool = False,
    ) -> dict[str, Any]:
        """Kick off background generation for a level; reuse valid ready sets."""
        key = self._entry_key(user_id, level_id)
        async with self._lock:
            self._prune_user(user_id, protect_level_id=level_id)
            entry = self._cache.get(key)
            if entry and not self._stale(entry):
                if entry.status in ("fetching", "ready") and not force:
                    logger.info(
                        "[PhasePrefetch] reuse user=%s level=%s status=%s",
                        user_id,
                        level_id,
                        entry.status,
                    )
                    return self._status_payload(entry, level_id=level_id)
                if entry.status == "error" and not force and entry.retried:
                    return self._status_payload(entry, level_id=level_id)

            self._cache[key] = PrefetchEntry(
                status="fetching",
                level_id=level_id,
                format_version=self._current_format(),
                started_at=time.time(),
            )
            self._prune_user(user_id, protect_level_id=level_id)

        asyncio.create_task(self._run(user_id, level_id))
        logger.info("[PhasePrefetch] started user=%s level=%s", user_id, level_id)
        return await self.status(user_id, level_id)

    async def start_many(
        self,
        user_id: uuid.UUID,
        level_ids: list[int],
        *,
        force: bool = False,
    ) -> dict[str, Any]:
        """Fill / top up the rolling buffer for several upcoming levels."""
        started: list[int] = []
        statuses: list[dict[str, Any]] = []
        # Cap to buffer size — modest rolling window only
        for level_id in level_ids[: self._buffer_size()]:
            st = await self.start(user_id, level_id, force=force)
            started.append(level_id)
            statuses.append(st)
        buffer = await self.buffer_status(user_id)
        return {
            "warmed": started,
            "buffer": statuses,
            "ready_count": len(buffer.get("ready_levels") or []),
            "fetching_count": len(buffer.get("fetching_levels") or []),
            "question_count": buffer.get("question_count") or 0,
            "status": buffer.get("status") or "idle",
        }

    async def claim(
        self,
        user_id: uuid.UUID,
        level_id: int,
    ) -> dict[str, Any] | None:
        """
        Consume a ready prefetch for this level only (other buffer slots remain).
        Returns {questions, mix, phase_number, level_number, format_version} or None.
        """
        key = self._entry_key(user_id, level_id)
        async with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if self._stale(entry):
                self._cache.pop(key, None)
                return None
            if entry.status != "ready" or not entry.questions:
                return None
            payload = {
                "questions": list(entry.questions),
                "mix": dict(entry.mix),
                "phase_number": entry.phase_number,
                "level_number": entry.level_number,
                "format_version": entry.format_version,
            }
            self._cache.pop(key, None)
            logger.info(
                "[PhasePrefetch] claimed user=%s level=%s questions=%s buffer_left=%s",
                user_id,
                level_id,
                len(payload["questions"]),
                len(self._user_entries(user_id)),
            )
            return payload

    async def wait_until_ready(
        self,
        user_id: uuid.UUID,
        level_id: int,
        *,
        timeout_s: float = 55.0,
        poll_s: float = 0.5,
    ) -> bool:
        """Poll until a buffered level is ready (does not claim)."""
        deadline = time.time() + max(0.0, timeout_s)
        while time.time() <= deadline:
            st = await self.status(user_id, level_id)
            status = st.get("status")
            if status == "ready" and int(st.get("question_count") or 0) > 0:
                return True
            if status == "error":
                return False
            if status == "idle":
                # Not started / expired
                return False
            await asyncio.sleep(poll_s)
        return False

    async def claim_or_wait(
        self,
        user_id: uuid.UUID,
        level_id: int,
        *,
        timeout_s: float = 75.0,
        poll_s: float = 0.4,
    ) -> dict[str, Any] | None:
        """Claim a ready prefetch, or wait briefly if generation is already in flight."""
        ready = await self.claim(user_id, level_id)
        if ready:
            return ready

        key = self._entry_key(user_id, level_id)
        entry = self._cache.get(key)
        if not entry or entry.status != "fetching":
            return None

        deadline = time.time() + max(1.0, timeout_s)
        logger.info(
            "[PhasePrefetch] waiting for in-flight user=%s level=%s timeout=%.0fs",
            user_id,
            level_id,
            timeout_s,
        )
        while time.time() < deadline:
            await asyncio.sleep(poll_s)
            ready = await self.claim(user_id, level_id)
            if ready:
                return ready
            entry = self._cache.get(key)
            if not entry:
                return None
            if entry.status == "error":
                return None
            if entry.status not in ("fetching", "ready"):
                return None
        return await self.claim(user_id, level_id)

    def reserved_stems(
        self,
        user_id: uuid.UUID,
        *,
        exclude_level_id: int | None = None,
    ) -> set[str]:
        """Stems already held in this learner's buffer (ready levels)."""
        from app.phases.adaptive import normalize_question_text

        stems: set[str] = set()
        for _key, entry in self._user_entries(user_id):
            if exclude_level_id is not None and entry.level_id == exclude_level_id:
                continue
            if entry.status != "ready" or not entry.questions:
                continue
            for q in entry.questions:
                stems.add(
                    normalize_question_text(str(q.get("question_text") or ""))
                )
        return stems

    async def _run(self, user_id: uuid.UUID, level_id: int) -> None:
        key = self._entry_key(user_id, level_id)
        # One build at a time per user → later levels exclude earlier buffer stems.
        async with self._user_build_lock(user_id):
            try:
                from app.database import AsyncSessionLocal
                from app.phases.service import build_level_question_set

                extra_exclude = self.reserved_stems(
                    user_id, exclude_level_id=level_id
                )
                async with AsyncSessionLocal() as db:
                    built = await build_level_question_set(
                        db,
                        user_id,
                        level_id,
                        extra_exclude_texts=extra_exclude or None,
                    )
                    await db.commit()

                async with self._lock:
                    current = self._cache.get(key)
                    if (
                        not current
                        or current.level_id != level_id
                        or current.status != "fetching"
                    ):
                        return
                    current.status = "ready"
                    current.questions = built["questions"]
                    current.mix = built["mix"]
                    current.phase_number = built["phase_number"]
                    current.level_number = built["level_number"]
                    current.format_version = built["format_version"]
                    current.ready_at = time.time()
                    current.error = None
                logger.info(
                    "[PhasePrefetch] ready user=%s level=%s count=%s excluded=%s in %.1fs",
                    user_id,
                    level_id,
                    len(built["questions"]),
                    len(extra_exclude),
                    time.time() - (current.started_at or time.time()),
                )
            except Exception as exc:
                logger.exception(
                    "[PhasePrefetch] failed user=%s level=%s", user_id, level_id
                )
                async with self._lock:
                    current = self._cache.get(key)
                    if current and current.level_id == level_id:
                        if not current.retried:
                            current.retried = True
                            current.status = "fetching"
                            current.error = None
                            current.started_at = time.time()
                            asyncio.create_task(self._run(user_id, level_id))
                            logger.info(
                                "[PhasePrefetch] retrying once user=%s level=%s",
                                user_id,
                                level_id,
                            )
                            return
                        current.status = "error"
                        current.error = str(exc)[:240]


phase_prefetch_manager = PhasePrefetchManager()


def schedule_buffer_warm(
    user_id: uuid.UUID,
    *,
    anchor_level_id: int | None = None,
) -> None:
    """Fire-and-forget buffer top-up (own DB session). Safe from request handlers."""

    async def _job() -> None:
        try:
            from app.database import AsyncSessionLocal
            from app.phases.service import warm_prefetch_buffer

            async with AsyncSessionLocal() as db:
                result = await warm_prefetch_buffer(
                    db, user_id, anchor_level_id=anchor_level_id
                )
                await db.commit()
            logger.info(
                "[PhasePrefetch] buffer warm user=%s warmed=%s ready=%s fetching=%s",
                user_id,
                result.get("warmed"),
                result.get("ready_count"),
                result.get("fetching_count"),
            )
        except Exception:
            logger.exception(
                "[PhasePrefetch] buffer warm failed user=%s anchor=%s",
                user_id,
                anchor_level_id,
            )

    try:
        asyncio.get_running_loop().create_task(_job())
    except RuntimeError:
        # No running loop (unlikely in FastAPI) — skip silently
        logger.debug("[PhasePrefetch] no event loop for buffer warm")
