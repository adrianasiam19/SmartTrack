"""Phase / Level progression + mixed-subject challenge sessions."""
from __future__ import annotations

import asyncio
import logging
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.assessment.models import ChallengeResponse, ChallengeSession
from app.config import settings
from app.phases.adaptive import (
    AdaptiveConfig,
    bump_adjustment_if_strong,
    effective_difficulty,
    expand_subject_queue,
    level_question_count,
    next_adjustment,
    normalize_question_text,
    should_nudge_learning,
    subject_mix_for_level,
    update_rolling_accuracy,
    update_weak_streak,
)
from app.phases.models import Level, Phase, UserLevelProgress, UserPhaseProgress, UserSubjectPerformance
from app.phases.question_gen import generate_subject_question, plan_types_for_subjects
from app.users.gamification import apply_xp, rank_for_xp, record_daily_challenge_streak
from app.users.models import User

logger = logging.getLogger(__name__)

SUBJECTS = ("english", "core_maths", "integrated_science", "social_studies")
XP_PER_CORRECT = 10


def _adaptive_cfg() -> AdaptiveConfig:
    return AdaptiveConfig(
        rolling_window=settings.DIFFICULTY_ROLLING_WINDOW,
        low_accuracy=settings.DIFFICULTY_LOW_ACCURACY,
        high_accuracy=settings.DIFFICULTY_HIGH_ACCURACY,
        adj_step=settings.DIFFICULTY_ADJ_STEP,
        difficulty_min=settings.DIFFICULTY_MIN,
        difficulty_max=settings.DIFFICULTY_MAX,
        learning_nudge_levels=settings.LEARNING_NUDGE_LEVELS,
    )


async def ensure_user_progression(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Create locked/unlocked progress rows for all phases/levels if missing."""
    phases = (
        await db.execute(select(Phase).options(selectinload(Phase.levels)).order_by(Phase.number))
    ).scalars().all()
    if not phases:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Phases not seeded")

    for phase in phases:
        upp = (
            await db.execute(
                select(UserPhaseProgress).where(
                    UserPhaseProgress.user_id == user_id,
                    UserPhaseProgress.phase_id == phase.id,
                )
            )
        ).scalar_one_or_none()
        if not upp:
            status_val = "in_progress" if phase.number == 1 else "locked"
            upp = UserPhaseProgress(
                user_id=user_id,
                phase_id=phase.id,
                status=status_val,
                started_at=datetime.now(timezone.utc) if phase.number == 1 else None,
            )
            db.add(upp)

        for level in phase.levels:
            ulp = (
                await db.execute(
                    select(UserLevelProgress).where(
                        UserLevelProgress.user_id == user_id,
                        UserLevelProgress.level_id == level.id,
                    )
                )
            ).scalar_one_or_none()
            if not ulp:
                lvl_status = "locked"
                if phase.number == 1 and level.number == 1:
                    lvl_status = "available"
                ulp = UserLevelProgress(
                    user_id=user_id,
                    level_id=level.id,
                    status=lvl_status,
                )
                db.add(ulp)
    await db.commit()


async def get_progression(db: AsyncSession, user_id: uuid.UUID) -> dict[str, Any]:
    await ensure_user_progression(db, user_id)
    phases = (
        await db.execute(select(Phase).options(selectinload(Phase.levels)).order_by(Phase.number))
    ).scalars().all()

    phase_prog = {
        p.phase_id: p
        for p in (
            await db.execute(select(UserPhaseProgress).where(UserPhaseProgress.user_id == user_id))
        ).scalars().all()
    }
    level_prog = {
        p.level_id: p
        for p in (
            await db.execute(select(UserLevelProgress).where(UserLevelProgress.user_id == user_id))
        ).scalars().all()
    }

    result_phases = []
    current_phase = 1
    current_level = 1
    for phase in phases:
        pp = phase_prog.get(phase.id)
        levels_out = []
        for level in sorted(phase.levels, key=lambda L: L.number):
            lp = level_prog.get(level.id)
            st = lp.status if lp else "locked"
            levels_out.append(
                {
                    "id": level.id,
                    "number": level.number,
                    "difficulty_baseline": level.difficulty_baseline,
                    "status": st,
                    "score": lp.score if lp else None,
                    "attempts": lp.attempts if lp else 0,
                    "completed_at": lp.completed_at if lp else None,
                }
            )
            if st in ("available", "in_progress"):
                current_phase = phase.number
                current_level = level.number
            elif st == "completed" and phase.number >= current_phase:
                current_phase = phase.number
                current_level = min(level.number + 1, 10)

        result_phases.append(
            {
                "id": phase.id,
                "number": phase.number,
                "name": phase.name,
                "description": phase.description,
                "status": pp.status if pp else "locked",
                "levels": levels_out,
            }
        )

    return {
        "phases": result_phases,
        "current_phase_number": current_phase,
        "current_level_number": current_level,
    }


async def _get_or_create_subject_perf(
    db: AsyncSession, user_id: uuid.UUID, subject: str
) -> UserSubjectPerformance:
    row = (
        await db.execute(
            select(UserSubjectPerformance).where(
                UserSubjectPerformance.user_id == user_id,
                UserSubjectPerformance.subject == subject,
            )
        )
    ).scalar_one_or_none()
    if not row:
        row = UserSubjectPerformance(user_id=user_id, subject=subject)
        db.add(row)
        await db.flush()
    return row


async def build_level_question_set(
    db: AsyncSession,
    user_id: uuid.UUID,
    level_id: int,
    *,
    extra_exclude_texts: set[str] | None = None,
) -> dict[str, Any]:
    """
    Build a full question payload for a level WITHOUT creating a ChallengeSession.

    Stage 4: every question completes image analysis → plan → retrieve → write
    (or text-only) BEFORE this function returns. The learner never sees a
    question that later swaps its image or stem mid-session.

    Used by live start (cache miss) and background prefetch. Questions are generated
    in parallel (bounded concurrency) to cut wall-clock wait.

    extra_exclude_texts: optional stems already reserved in the prefetch buffer
    for this learner (other levels) so parallel buffer fills do not duplicate.
    """
    await ensure_user_progression(db, user_id)
    level = (
        await db.execute(select(Level).options(selectinload(Level.phase)).where(Level.id == level_id))
    ).scalar_one_or_none()
    if not level:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Level not found")

    phase = level.phase
    phase_floor = 1
    cfg = _adaptive_cfg()
    question_budget = level_question_count(level.number)

    accuracies: dict[str, float] = {}
    for subject in SUBJECTS:
        perf = await _get_or_create_subject_perf(db, user_id, subject)
        accuracies[subject] = float(perf.rolling_accuracy)
    mix = subject_mix_for_level(level.number, accuracies, list(SUBJECTS))

    used_bank_ids: set[str] = set()
    used_texts: set[str] = set()
    history_limit = max(20, int(getattr(settings, "CHALLENGE_EXCLUDE_HISTORY", 80)))
    prior = (
        await db.execute(
            select(ChallengeResponse.question_text)
            .where(ChallengeResponse.user_id == user_id)
            .order_by(ChallengeResponse.id.desc())
            .limit(history_limit)
        )
    ).scalars().all()
    for text in prior:
        used_texts.add(normalize_question_text(str(text or "")))
    if extra_exclude_texts:
        for text in extra_exclude_texts:
            used_texts.add(normalize_question_text(str(text or "")))

    rng = random.Random()
    subject_queue = expand_subject_queue(mix, rng)

    eff_by_subject: dict[str, int] = {}
    perf_summary_parts: list[str] = []
    for subject in mix:
        if mix[subject] <= 0:
            continue
        perf = await _get_or_create_subject_perf(db, user_id, subject)
        eff = effective_difficulty(
            level.difficulty_baseline,
            perf.current_difficulty_adjustment,
            phase_floor=phase_floor,
            cfg=cfg,
        )
        eff_by_subject[subject] = eff
        perf_summary_parts.append(
            f"{subject}: accuracy={perf.rolling_accuracy:.2f}, count={mix[subject]}, "
            f"eff_difficulty={eff}"
        )
    performance_summary = (
        f"Level {level.number} asks {question_budget} questions total. "
        + "; ".join(perf_summary_parts)
    )

    concurrency = max(1, int(getattr(settings, "CHALLENGE_GEN_CONCURRENCY", 4)))
    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    planned_types = plan_types_for_subjects(subject_queue, rng)

    async def _one(
        slot: int, subject: str, forced_type: str
    ) -> tuple[int, str, dict[str, Any], int]:
        eff = eff_by_subject[subject]
        async with sem:
            async with lock:
                local_bank = set(used_bank_ids)
                local_texts = set(used_texts)
            generated = await generate_subject_question(
                phase_number=phase.number,
                level_number=level.number,
                subject=subject,
                effective_difficulty=eff,
                performance_summary=performance_summary,
                question_budget=question_budget,
                exclude_bank_ids=local_bank,
                exclude_texts=local_texts,
                rng=random.Random(rng.randint(1, 10_000_000) + slot),
                forced_type=forced_type,
            )
            norm = normalize_question_text(generated["question_text"])
            needs_retry = False
            async with lock:
                if norm in used_texts:
                    needs_retry = True
                    retry_bank = set(used_bank_ids)
                    retry_texts = set(used_texts)
                else:
                    bank_id = generated.get("bank_id")
                    if bank_id:
                        used_bank_ids.add(str(bank_id))
                    used_texts.add(norm)
                    return slot, subject, generated, eff

            if needs_retry:
                regenerated = await generate_subject_question(
                    phase_number=phase.number,
                    level_number=level.number,
                    subject=subject,
                    effective_difficulty=eff,
                    performance_summary=performance_summary,
                    question_budget=question_budget,
                    exclude_bank_ids=retry_bank,
                    exclude_texts=retry_texts,
                    rng=random.Random(rng.randint(1, 10_000_000) + slot + 99),
                    forced_type=forced_type,
                )
                async with lock:
                    bank_id = regenerated.get("bank_id")
                    if bank_id:
                        used_bank_ids.add(str(bank_id))
                    used_texts.add(normalize_question_text(regenerated["question_text"]))
                return slot, subject, regenerated, eff
            return slot, subject, generated, eff

    started = time.time()
    results = await asyncio.gather(
        *[
            _one(i, subject, planned_types[i] if i < len(planned_types) else "mcq")
            for i, subject in enumerate(subject_queue)
        ]
    )
    results_sorted = sorted(results, key=lambda row: row[0])
    questions: list[dict[str, Any]] = []
    for slot, subject, generated, eff in results_sorted:
        questions.append(
            {
                "subject": subject,
                "question_index": slot,
                "question_text": generated["question_text"],
                "question_type": generated.get("question_type", "mcq"),
                "options": generated.get("options"),
                "correct_answer": str(generated["correct_answer"]),
                "difficulty": eff,
                "explanation": generated.get("explanation"),
                "image": (generated.get("options") or {}).get("image")
                if isinstance(generated.get("options"), dict)
                else generated.get("image"),
            }
        )

    logger.info(
        "Built %s questions for level=%s user=%s in %.1fs (concurrency=%s)",
        len(questions),
        level_id,
        user_id,
        time.time() - started,
        concurrency,
    )
    return {
        "questions": questions,
        "mix": mix,
        "phase_number": phase.number,
        "level_number": level.number,
        "format_version": int(getattr(settings, "CHALLENGE_FORMAT_VERSION", 10)),
        "level": level,
    }


async def start_level(
    db: AsyncSession,
    user_id: uuid.UUID,
    level_id: int,
    *,
    replay: bool = False,
) -> dict[str, Any]:
    await ensure_user_progression(db, user_id)
    level = (
        await db.execute(select(Level).options(selectinload(Level.phase)).where(Level.id == level_id))
    ).scalar_one_or_none()
    if not level:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Level not found")

    ulp = (
        await db.execute(
            select(UserLevelProgress).where(
                UserLevelProgress.user_id == user_id,
                UserLevelProgress.level_id == level_id,
            )
        )
    ).scalar_one_or_none()
    if not ulp:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Progress not initialized")

    if replay:
        if ulp.status != "completed":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only completed levels can be replayed")
    else:
        if ulp.status not in ("available", "in_progress", "completed"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Level is locked")

    phase = level.phase
    from_prefetch = False
    mix: dict[str, int] = {}
    draft_questions: list[dict[str, Any]] = []

    # Claim background prefetch when available (skips LLM wait).
    # If prefetch is still in flight, wait briefly instead of starting a duplicate generation.
    if not replay:
        try:
            from app.phases.prefetch import phase_prefetch_manager

            wait_s = float(getattr(settings, "CHALLENGE_PREFETCH_WAIT_SECONDS", 75))
            claimed = await phase_prefetch_manager.claim_or_wait(
                user_id, level_id, timeout_s=wait_s
            )
            if claimed and claimed.get("questions"):
                draft_questions = claimed["questions"]
                mix = claimed.get("mix") or {}
                from_prefetch = True
                logger.info(
                    "start_level using prefetch user=%s level=%s count=%s",
                    user_id,
                    level_id,
                    len(draft_questions),
                )
        except Exception:
            logger.exception("Prefetch claim failed; falling back to live generation")

    if not draft_questions:
        from app.phases.prefetch import phase_prefetch_manager

        extra = phase_prefetch_manager.reserved_stems(
            user_id, exclude_level_id=level_id
        )
        built = await build_level_question_set(
            db,
            user_id,
            level_id,
            extra_exclude_texts=extra or None,
        )
        draft_questions = built["questions"]
        mix = built["mix"]
        level = built["level"]
        phase = level.phase

    session = ChallengeSession(
        user_id=user_id,
        challenge_level=min(level.number, 3),
        level_id=level.id,
        is_replay=replay,
        status="in_progress",
    )
    db.add(session)
    await db.flush()

    questions_out: list[dict[str, Any]] = []
    for q_index, item in enumerate(draft_questions):
        resp = ChallengeResponse(
            session_id=session.id,
            user_id=user_id,
            subject=str(item.get("subject") or "english"),
            question_index=q_index,
            question_text=str(item["question_text"]),
            question_type=str(item.get("question_type") or "mcq"),
            options=item.get("options"),
            correct_answer=str(item.get("correct_answer") or ""),
            difficulty=item.get("difficulty"),
            explanation=item.get("explanation"),
        )
        db.add(resp)
        await db.flush()
        options = resp.options if isinstance(resp.options, dict) else {}
        from app.media.learner_media import to_learner_image

        raw_image = options.get("image") or item.get("image")
        safe_image = to_learner_image(raw_image if isinstance(raw_image, dict) else None)
        # Keep options educational (legend) but scrub nested image attribution
        safe_options = options
        if isinstance(options, dict) and isinstance(options.get("image"), dict):
            safe_options = dict(options)
            scrubbed = to_learner_image(options["image"])
            if scrubbed:
                if isinstance(options["image"].get("legend"), dict):
                    scrubbed = {**scrubbed, "legend": options["image"]["legend"]}
                safe_options["image"] = scrubbed
            else:
                safe_options.pop("image", None)
        questions_out.append(
            {
                "id": resp.id,
                "subject": resp.subject,
                "question_index": q_index,
                "question_text": resp.question_text,
                "question_type": resp.question_type,
                "options": safe_options,
                "difficulty": resp.difficulty,
                "image": safe_image,
            }
        )

    if not replay and ulp.status == "available":
        ulp.status = "in_progress"
    ulp.attempts = (ulp.attempts or 0) + 1
    await db.commit()

    # Stage 4 — after claiming/starting, top up the rolling buffer for upcoming levels.
    if not replay:
        try:
            from app.phases.prefetch import schedule_buffer_warm

            schedule_buffer_warm(user_id, anchor_level_id=level.id)
        except Exception:
            logger.debug("Could not schedule prefetch buffer warm", exc_info=True)

    return {
        "session_id": session.id,
        "level_id": level.id,
        "phase_number": phase.number,
        "level_number": level.number,
        "is_replay": replay,
        "format_version": int(getattr(settings, "CHALLENGE_FORMAT_VERSION", 10)),
        "question_count": len(questions_out),
        "subject_mix": mix,
        "from_prefetch": from_prefetch,
        "questions": questions_out,
    }


async def prefetch_level(
    db: AsyncSession,
    user_id: uuid.UUID,
    level_id: int,
) -> dict[str, Any]:
    """Validate access and kick off background question generation for a level."""
    await ensure_user_progression(db, user_id)
    level = (
        await db.execute(select(Level).where(Level.id == level_id))
    ).scalar_one_or_none()
    if not level:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Level not found")

    ulp = (
        await db.execute(
            select(UserLevelProgress).where(
                UserLevelProgress.user_id == user_id,
                UserLevelProgress.level_id == level_id,
            )
        )
    ).scalar_one_or_none()
    if not ulp:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Progress not initialized")

    # Allow prefetch for the next locked level if the previous level is completed/in progress
    if ulp.status == "locked":
        prev = (
            await db.execute(
                select(Level).where(
                    Level.phase_id == level.phase_id,
                    Level.number == level.number - 1,
                )
            )
        ).scalar_one_or_none()
        if not prev:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Level is locked")
        prev_ulp = (
            await db.execute(
                select(UserLevelProgress).where(
                    UserLevelProgress.user_id == user_id,
                    UserLevelProgress.level_id == prev.id,
                )
            )
        ).scalar_one_or_none()
        if not prev_ulp or prev_ulp.status not in ("completed", "in_progress", "available"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Level is locked")

    from app.phases.prefetch import phase_prefetch_manager

    return await phase_prefetch_manager.start(user_id, level_id)


async def prefetch_status(
    user_id: uuid.UUID,
    level_id: int,
) -> dict[str, Any]:
    from app.phases.prefetch import phase_prefetch_manager

    return await phase_prefetch_manager.status(user_id, level_id)


async def _ordered_levels(db: AsyncSession) -> list[Level]:
    phases = (
        await db.execute(select(Phase).options(selectinload(Phase.levels)).order_by(Phase.number))
    ).scalars().all()
    out: list[Level] = []
    for phase in phases:
        levels = sorted(phase.levels or [], key=lambda lv: lv.number)
        out.extend(levels)
    return out


async def upcoming_prefetch_targets(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    anchor_level_id: int | None = None,
    count: int | None = None,
) -> list[int]:
    """
    Resolve the next N level ids to keep in the rolling buffer.

    Prefer: current playable (available/in_progress), then the following levels
    in phase order (including the immediate locked next level).
    """
    await ensure_user_progression(db, user_id)
    limit = count or max(1, int(getattr(settings, "CHALLENGE_PREFETCH_BUFFER_LEVELS", 3)))
    levels = await _ordered_levels(db)
    if not levels:
        return []

    progress_rows = (
        await db.execute(select(UserLevelProgress).where(UserLevelProgress.user_id == user_id))
    ).scalars().all()
    status_by_id = {row.level_id: row.status for row in progress_rows}

    start_idx = 0
    if anchor_level_id is not None:
        for i, lv in enumerate(levels):
            if lv.id == anchor_level_id:
                # Warm levels *after* the one being played / just started
                start_idx = i + 1
                break
    else:
        # First available / in_progress; else first incomplete; else last
        found = None
        for i, lv in enumerate(levels):
            st = status_by_id.get(lv.id, "locked")
            if st in ("available", "in_progress"):
                found = i
                break
        if found is None:
            for i, lv in enumerate(levels):
                if status_by_id.get(lv.id) != "completed":
                    found = i
                    break
        start_idx = found if found is not None else 0

    targets: list[int] = []
    for lv in levels[start_idx : start_idx + limit]:
        st = status_by_id.get(lv.id, "locked")
        # Prefetch current playable, next locked (allowed by prefetch_level), and completed (replay warm skip)
        if st == "completed":
            continue
        targets.append(lv.id)
        if len(targets) >= limit:
            break

    # If anchor was mid-phase and we skipped completed, still fill window
    if len(targets) < limit:
        for lv in levels[start_idx:]:
            if lv.id in targets:
                continue
            if status_by_id.get(lv.id) == "completed":
                continue
            targets.append(lv.id)
            if len(targets) >= limit:
                break

    return targets[:limit]


def _can_prefetch_locked(
    ulp_status: str,
    prev_status: str | None,
) -> bool:
    if ulp_status != "locked":
        return True
    return prev_status in ("completed", "in_progress", "available")


async def warm_prefetch_buffer(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    anchor_level_id: int | None = None,
) -> dict[str, Any]:
    """
    Top up the learner's rolling challenge buffer (next 2–3 levels).

    Safe to call from Dashboard / Challenges / after start_level.
    Reuses valid ready sets; only generates missing slots.
    """
    from app.phases.prefetch import phase_prefetch_manager

    targets = await upcoming_prefetch_targets(
        db, user_id, anchor_level_id=anchor_level_id
    )
    # When no anchor, also include the current playable level itself
    if anchor_level_id is None:
        levels = await _ordered_levels(db)
        progress_rows = (
            await db.execute(
                select(UserLevelProgress).where(UserLevelProgress.user_id == user_id)
            )
        ).scalars().all()
        status_by_id = {row.level_id: row.status for row in progress_rows}
        current_ids = [
            lv.id
            for lv in levels
            if status_by_id.get(lv.id) in ("available", "in_progress")
        ][:1]
        merged: list[int] = []
        for lid in current_ids + targets:
            if lid not in merged:
                merged.append(lid)
        targets = merged[
            : max(1, int(getattr(settings, "CHALLENGE_PREFETCH_BUFFER_LEVELS", 3)))
        ]

    warmed: list[int] = []
    primary_id: int | None = targets[0] if targets else None

    async def _start_one(level_id: int) -> bool:
        try:
            level = (
                await db.execute(select(Level).where(Level.id == level_id))
            ).scalar_one_or_none()
            if not level:
                return False
            ulp = (
                await db.execute(
                    select(UserLevelProgress).where(
                        UserLevelProgress.user_id == user_id,
                        UserLevelProgress.level_id == level_id,
                    )
                )
            ).scalar_one_or_none()
            if not ulp:
                return False
            if ulp.status == "locked":
                prev = (
                    await db.execute(
                        select(Level).where(
                            Level.phase_id == level.phase_id,
                            Level.number == level.number - 1,
                        )
                    )
                ).scalar_one_or_none()
                prev_status = None
                if prev:
                    prev_ulp = (
                        await db.execute(
                            select(UserLevelProgress).where(
                                UserLevelProgress.user_id == user_id,
                                UserLevelProgress.level_id == prev.id,
                            )
                        )
                    ).scalar_one_or_none()
                    prev_status = prev_ulp.status if prev_ulp else None
                if not _can_prefetch_locked(ulp.status, prev_status):
                    return False

            await phase_prefetch_manager.start(user_id, level_id)
            return True
        except Exception:
            logger.debug(
                "warm_prefetch skip level=%s user=%s", level_id, user_id, exc_info=True
            )
            return False

    # Prefer the current playable level first so Start can claim a ready set.
    if primary_id is not None and await _start_one(primary_id):
        warmed.append(primary_id)
        wait_s = float(getattr(settings, "CHALLENGE_PREFETCH_WARM_WAIT_SECONDS", 55))
        if wait_s > 0:
            ready = await phase_prefetch_manager.wait_until_ready(
                user_id, primary_id, timeout_s=wait_s
            )
            logger.info(
                "[PhasePrefetch] warm primary user=%s level=%s ready=%s wait=%.0fs",
                user_id,
                primary_id,
                ready,
                wait_s,
            )

    for level_id in targets[1:]:
        if await _start_one(level_id):
            warmed.append(level_id)

    buffer = await phase_prefetch_manager.buffer_status(user_id)
    return {
        "warmed": warmed,
        "buffer": buffer.get("buffer") or [],
        "ready_count": len(buffer.get("ready_levels") or []),
        "fetching_count": len(buffer.get("fetching_levels") or []),
        "question_count": buffer.get("question_count") or 0,
        "status": buffer.get("status") or "idle",
        "ready_levels": buffer.get("ready_levels") or [],
        "fetching_levels": buffer.get("fetching_levels") or [],
        "primary_ready": (
            primary_id in (buffer.get("ready_levels") or [])
            if primary_id is not None
            else False
        ),
    }


async def get_session_status(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: int,
) -> dict[str, Any]:
    session = (
        await db.execute(select(ChallengeSession).where(ChallengeSession.id == session_id))
    ).scalar_one_or_none()
    if not session or session.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")

    responses = (
        await db.execute(
            select(ChallengeResponse).where(ChallengeResponse.session_id == session_id)
        )
    ).scalars().all()
    answered = sum(1 for r in responses if r.user_answer is not None)
    return {
        "session_id": session.id,
        "status": session.status,
        "level_id": session.level_id,
        "is_replay": bool(session.is_replay),
        "answered_count": answered,
        "question_count": len(responses),
    }


async def submit_answer(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: int,
    question_id: int,
    answer: str,
    time_taken_seconds: float | None = None,
) -> dict[str, Any]:
    session = (
        await db.execute(select(ChallengeSession).where(ChallengeSession.id == session_id))
    ).scalar_one_or_none()
    if not session or session.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")

    q = (
        await db.execute(select(ChallengeResponse).where(ChallengeResponse.id == question_id))
    ).scalar_one_or_none()
    if not q or q.session_id != session_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")

    # Idempotent replay: after a slow/interrupted complete, the client may retry the
    # last question. Returning the prior result (even if the session is completed)
    # prevents the frontend from "recovering" into a brand-new Q1 session.
    if q.user_answer is not None:
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
        return {
            "is_correct": bool(q.is_correct),
            "explanation": q.explanation,
            "correct_count": session.correct_count,
            "wrong_count": session.wrong_count,
            "xp_earned": 0,
            "user_xp": user.xp or 0,
            "rank": user.rank,
            "streak": user.streak,
            "streak_incremented": False,
            "learning_nudge": None,
        }

    if session.status != "in_progress":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session is not active")

    from app.phases.answer_grading import grade_answer

    is_correct = grade_answer(
        question_type=q.question_type or "mcq",
        correct_answer=q.correct_answer or "",
        user_answer=answer,
        options=q.options if isinstance(q.options, dict) else None,
    )

    # Persist truncated answer for schema limits
    q.user_answer = answer[:4000]
    q.is_correct = is_correct
    q.time_taken_seconds = time_taken_seconds
    q.answered_at = datetime.now(timezone.utc)

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    xp_earned = 0
    prev_rank = user.rank or "Beginner"

    if is_correct:
        session.correct_count += 1
        q.xp_earned = XP_PER_CORRECT
        session.total_xp += XP_PER_CORRECT
        xp_earned, user_rank, user_xp = apply_xp(user, XP_PER_CORRECT)
    else:
        session.wrong_count += 1
        user.rank = rank_for_xp(user.xp or 0)
        user_rank = user.rank
        user_xp = user.xp or 0

    if user_rank != prev_rank and user_rank != "Beginner":
        try:
            from app.notifications.events import notify_badge_unlocked

            await notify_badge_unlocked(db, user_id, rank=user_rank)
        except Exception:
            logger.exception("Failed to create badge notification")

    # Any answered challenge question counts toward the daily activity streak.
    streak_info = record_daily_challenge_streak(user)
    if streak_info.get("incremented") and int(streak_info.get("streak") or 0) in (
        3,
        7,
        14,
        30,
    ):
        try:
            from app.notifications.events import notify_streak_milestone

            await notify_streak_milestone(
                db, user_id, streak=int(streak_info["streak"])
            )
        except Exception:
            logger.exception("Failed to create streak milestone notification")

    cfg = _adaptive_cfg()
    level = None
    phase_floor = 1
    baseline = 1
    if session.level_id:
        level = (
            await db.execute(select(Level).where(Level.id == session.level_id))
        ).scalar_one_or_none()
        if level:
            baseline = level.difficulty_baseline
            phase_floor = 1

    perf = await _get_or_create_subject_perf(db, user_id, q.subject)
    perf.rolling_accuracy = update_rolling_accuracy(
        perf.rolling_accuracy, is_correct, cfg.rolling_window
    )
    perf.current_difficulty_adjustment = next_adjustment(
        perf.current_difficulty_adjustment,
        perf.rolling_accuracy,
        phase_floor=phase_floor,
        baseline=baseline,
        cfg=cfg,
    )
    perf.updated_at = datetime.now(timezone.utc)

    nudge = None
    # weak streak updated on session complete; preview if already weak
    if should_nudge_learning(perf.weak_level_streak, cfg):
        from app.learning.service import suggest_topic_for_subject

        suggested = await suggest_topic_for_subject(db, q.subject)
        nudge = {
            "subject": q.subject,
            "message": f"Practice {q.subject.replace('_', ' ')} in Learning Center",
            "curriculum_id": suggested.curriculum_id if suggested else None,
            "topic_title": suggested.title if suggested else None,
        }

    await db.commit()
    return {
        "is_correct": is_correct,
        "explanation": q.explanation,
        "correct_count": session.correct_count,
        "wrong_count": session.wrong_count,
        "xp_earned": xp_earned,
        "user_xp": user_xp,
        "rank": user_rank,
        "streak": streak_info.get("streak"),
        "streak_incremented": streak_info.get("incremented"),
        "learning_nudge": nudge,
    }


async def complete_session(db: AsyncSession, user_id: uuid.UUID, session_id: int) -> dict[str, Any]:
    session = (
        await db.execute(select(ChallengeSession).where(ChallengeSession.id == session_id))
    ).scalar_one_or_none()
    if not session or session.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")

    # Idempotent: a refreshed tab / double-complete must not fail the learner.
    if session.status == "completed":
        level = None
        phase_number = None
        next_level_id = None
        next_level_number = None
        next_action = None
        if session.level_id:
            level = (
                await db.execute(
                    select(Level).options(selectinload(Level.phase)).where(Level.id == session.level_id)
                )
            ).scalar_one_or_none()
            if level:
                phase_number = level.phase.number
                next_level = (
                    await db.execute(
                        select(Level).where(
                            Level.phase_id == level.phase_id,
                            Level.number == level.number + 1,
                        )
                    )
                ).scalar_one_or_none()
                if next_level:
                    next_level_id = next_level.id
                    next_level_number = next_level.number
                else:
                    next_action = "psychometric_checkpoint"
        total = session.correct_count + session.wrong_count
        score = (session.correct_count / total) if total else 0.0
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
        return {
            "passed": True,
            "score": score,
            "threshold": 0.0,
            "level_completed": True,
            "next": next_action,
            "phase_number": phase_number,
            "level_id": session.level_id,
            "next_level_id": next_level_id,
            "next_level_number": next_level_number,
            "session_xp": session.total_xp,
            "user_xp": user.xp,
            "rank": user.rank,
            "streak": user.streak,
            "streak_incremented": False,
            "learning_nudge": None,
        }

    total = session.correct_count + session.wrong_count
    score = (session.correct_count / total) if total else 0.0
    # No pass/fail gate — learners always progress; difficulty adapts per subject.
    passed = True
    threshold = 0.0

    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc)

    level_completed = False
    next_action = None
    phase_number = None
    next_level_id: int | None = None
    next_level_number: int | None = None

    level = None
    if session.level_id:
        level = (
            await db.execute(
                select(Level).options(selectinload(Level.phase)).where(Level.id == session.level_id)
            )
        ).scalar_one_or_none()
        if level:
            phase_number = level.phase.number
            next_level = (
                await db.execute(
                    select(Level).where(
                        Level.phase_id == level.phase_id,
                        Level.number == level.number + 1,
                    )
                )
            ).scalar_one_or_none()
            if next_level:
                # Always expose next level for "Continue" navigation (including replays)
                next_level_id = next_level.id
                next_level_number = next_level.number
            else:
                next_action = "psychometric_checkpoint"

    if session.level_id and not session.is_replay and level:
        ulp = (
            await db.execute(
                select(UserLevelProgress).where(
                    UserLevelProgress.user_id == user_id,
                    UserLevelProgress.level_id == session.level_id,
                )
            )
        ).scalar_one_or_none()

        cfg = _adaptive_cfg()
        phase_floor = 1
        baseline = level.difficulty_baseline if level else 1
        # Update weak streaks + raise difficulty only for subjects done well this level.
        responses = (
            await db.execute(
                select(ChallengeResponse).where(ChallengeResponse.session_id == session_id)
            )
        ).scalars().all()
        by_subject: dict[str, list[bool]] = {}
        for r in responses:
            if r.is_correct is None:
                continue
            by_subject.setdefault(r.subject, []).append(bool(r.is_correct))
        for subject, results in by_subject.items():
            acc = sum(1 for x in results if x) / len(results)
            perf = await _get_or_create_subject_perf(db, user_id, subject)
            perf.weak_level_streak = update_weak_streak(perf.weak_level_streak, acc, cfg)
            # Strong in this subject → harder next level; weak → difficulty stays.
            perf.current_difficulty_adjustment = bump_adjustment_if_strong(
                perf.current_difficulty_adjustment,
                acc,
                phase_floor=phase_floor,
                baseline=baseline,
                cfg=cfg,
            )
            perf.updated_at = datetime.now(timezone.utc)

        if ulp:
            was_incomplete = ulp.status != "completed"
            ulp.status = "completed"
            ulp.score = score
            ulp.completed_at = datetime.now(timezone.utc)
            level_completed = was_incomplete

            if next_level_id and was_incomplete:
                nlp = (
                    await db.execute(
                        select(UserLevelProgress).where(
                            UserLevelProgress.user_id == user_id,
                            UserLevelProgress.level_id == next_level_id,
                        )
                    )
                ).scalar_one_or_none()
                if nlp and nlp.status == "locked":
                    nlp.status = "available"
            elif next_action == "psychometric_checkpoint":
                upp = (
                    await db.execute(
                        select(UserPhaseProgress).where(
                            UserPhaseProgress.user_id == user_id,
                            UserPhaseProgress.phase_id == level.phase_id,
                        )
                    )
                ).scalar_one_or_none()
                if upp and upp.status != "completed":
                    # Mark pending psycho — stay in_progress until checkpoint+rec
                    upp.status = "in_progress"

    await db.commit()

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    streak_info = record_daily_challenge_streak(user)

    if level_completed and phase_number is not None:
        try:
            from app.notifications.events import notify_level_completed

            level_num = 1
            if session.level_id:
                lvl = (
                    await db.execute(select(Level).where(Level.id == session.level_id))
                ).scalar_one_or_none()
                if lvl:
                    level_num = lvl.number
            await notify_level_completed(
                db,
                user_id,
                phase_number=phase_number,
                level_number=level_num,
                xp_earned=int(session.total_xp or 0),
                score=float(score) * 100.0,
            )
            # Last level of a phase → nudge toward checkpoint / recommendations
            if next_action == "psychometric_checkpoint":
                from app.notifications.events import notify_system

                await notify_system(
                    db,
                    user_id,
                    title="Phase levels complete",
                    message=(
                        f"You finished all levels in Phase {phase_number}. "
                        "Complete the psychometric checkpoint to unlock recommendations."
                    ),
                    data={
                        "event": "phase_levels_complete",
                        "phase_number": phase_number,
                        "href": "/challenges",
                    },
                )
        except Exception:
            logger.exception("Failed to create level-complete notification")

    await db.commit()

    # Stage 4 — keep next levels prepared after a level finishes.
    try:
        from app.phases.prefetch import schedule_buffer_warm

        schedule_buffer_warm(
            user_id,
            anchor_level_id=session.level_id or next_level_id,
        )
    except Exception:
        logger.debug("Could not schedule prefetch buffer after complete", exc_info=True)

    return {
        "passed": passed,
        "score": score,
        "threshold": threshold,
        "level_completed": level_completed,
        "next": next_action,
        "phase_number": phase_number,
        "level_id": session.level_id,
        "next_level_id": next_level_id,
        "next_level_number": next_level_number,
        "session_xp": session.total_xp,
        "user_xp": user.xp or 0,
        "rank": user.rank or rank_for_xp(user.xp or 0),
        "streak": streak_info.get("streak"),
        "streak_incremented": streak_info.get("incremented"),
    }


async def unlock_next_phase_after_recommendation(
    db: AsyncSession, user_id: uuid.UUID, phase_id: int
) -> None:
    """Call after psycho + recommendation for a phase."""
    upp = (
        await db.execute(
            select(UserPhaseProgress).where(
                UserPhaseProgress.user_id == user_id,
                UserPhaseProgress.phase_id == phase_id,
            )
        )
    ).scalar_one_or_none()
    phase = (await db.execute(select(Phase).where(Phase.id == phase_id))).scalar_one_or_none()
    if not phase:
        return

    if upp:
        upp.status = "completed"
        upp.completed_at = datetime.now(timezone.utc)
        try:
            from app.notifications.events import notify_phase_completed

            await notify_phase_completed(
                db,
                user_id,
                phase_number=phase.number,
                phase_name=phase.name,
            )
        except Exception:
            logger.exception("Failed to create phase-complete notification")

    next_phase = (
        await db.execute(select(Phase).where(Phase.number == phase.number + 1))
    ).scalar_one_or_none()
    if next_phase:
        npp = (
            await db.execute(
                select(UserPhaseProgress).where(
                    UserPhaseProgress.user_id == user_id,
                    UserPhaseProgress.phase_id == next_phase.id,
                )
            )
        ).scalar_one_or_none()
        if npp and npp.status == "locked":
            npp.status = "in_progress"
            npp.started_at = datetime.now(timezone.utc)
        first_level = (
            await db.execute(
                select(Level).where(Level.phase_id == next_phase.id, Level.number == 1)
            )
        ).scalar_one_or_none()
        if first_level:
            flp = (
                await db.execute(
                    select(UserLevelProgress).where(
                        UserLevelProgress.user_id == user_id,
                        UserLevelProgress.level_id == first_level.id,
                    )
                )
            ).scalar_one_or_none()
            if flp and flp.status == "locked":
                flp.status = "available"
    await db.commit()
