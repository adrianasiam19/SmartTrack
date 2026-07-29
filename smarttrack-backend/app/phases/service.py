"""Phase / Level progression + mixed-subject challenge sessions."""
from __future__ import annotations

import logging
import random
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
from app.phases.question_gen import generate_subject_question
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
    phase_floor = 1  # Level 1 baseline within phase
    cfg = _adaptive_cfg()

    # Per-level question budget: L1–5 → 5, L6–7 → 6, L8–10 → 10
    question_budget = level_question_count(level.number)
    accuracies: dict[str, float] = {}
    for subject in SUBJECTS:
        perf = await _get_or_create_subject_perf(db, user_id, subject)
        accuracies[subject] = float(perf.rolling_accuracy)
    mix = subject_mix_for_level(level.number, accuracies, list(SUBJECTS))

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
    q_index = 0
    used_bank_ids: set[str] = set()
    used_texts: set[str] = set()

    # Avoid repeating questions the learner already saw in recent sessions.
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

    rng = random.Random()
    subject_queue = expand_subject_queue(mix, rng)

    # Per-subject effective difficulty + performance summary for prompts
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

    for subject in subject_queue:
        eff = eff_by_subject[subject]
        generated = await generate_subject_question(
            phase_number=phase.number,
            level_number=level.number,
            subject=subject,
            effective_difficulty=eff,
            performance_summary=performance_summary,
            question_budget=question_budget,
            exclude_bank_ids=used_bank_ids,
            exclude_texts=used_texts,
            rng=rng,
        )
        bank_id = generated.get("bank_id")
        if bank_id:
            used_bank_ids.add(str(bank_id))
        used_texts.add(normalize_question_text(generated["question_text"]))
        resp = ChallengeResponse(
            session_id=session.id,
            user_id=user_id,
            subject=subject,
            question_index=q_index,
            question_text=generated["question_text"],
            question_type=generated.get("question_type", "mcq"),
            options=generated.get("options"),
            correct_answer=str(generated["correct_answer"])[:500],
            difficulty=eff,
            explanation=generated.get("explanation"),
        )
        db.add(resp)
        await db.flush()
        questions_out.append(
            {
                "id": resp.id,
                "subject": subject,
                "question_index": q_index,
                "question_text": resp.question_text,
                "question_type": resp.question_type,
                "options": resp.options,
                "difficulty": eff,
                "image": (resp.options or {}).get("image")
                if isinstance(resp.options, dict)
                else None,
            }
        )
        q_index += 1

    if not replay and ulp.status == "available":
        ulp.status = "in_progress"
    ulp.attempts = (ulp.attempts or 0) + 1
    await db.commit()

    return {
        "session_id": session.id,
        "level_id": level.id,
        "phase_number": phase.number,
        "level_number": level.number,
        "is_replay": replay,
        "format_version": int(getattr(settings, "CHALLENGE_FORMAT_VERSION", 2)),
        "question_count": len(questions_out),
        "subject_mix": mix,
        "questions": questions_out,
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
    if session.status != "in_progress":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session is not active")

    q = (
        await db.execute(select(ChallengeResponse).where(ChallengeResponse.id == question_id))
    ).scalar_one_or_none()
    if not q or q.session_id != session_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")
    if q.user_answer is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already answered")

    from app.phases.answer_grading import grade_answer

    is_correct = grade_answer(
        question_type=q.question_type or "mcq",
        correct_answer=q.correct_answer or "",
        user_answer=answer,
        options=q.options if isinstance(q.options, dict) else None,
    )

    # Persist truncated answer for schema limits
    q.user_answer = answer[:500]
    q.is_correct = is_correct
    q.time_taken_seconds = time_taken_seconds
    q.answered_at = datetime.now(timezone.utc)

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    xp_earned = 0

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

    # Any answered challenge question counts toward the daily activity streak.
    streak_info = record_daily_challenge_streak(user)

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

    if session.level_id and not session.is_replay:
        ulp = (
            await db.execute(
                select(UserLevelProgress).where(
                    UserLevelProgress.user_id == user_id,
                    UserLevelProgress.level_id == session.level_id,
                )
            )
        ).scalar_one_or_none()
        level = (
            await db.execute(
                select(Level).options(selectinload(Level.phase)).where(Level.id == session.level_id)
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

        if ulp and level:
            was_incomplete = ulp.status != "completed"
            ulp.status = "completed"
            ulp.score = score
            ulp.completed_at = datetime.now(timezone.utc)
            level_completed = was_incomplete
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
                if was_incomplete:
                    nlp = (
                        await db.execute(
                            select(UserLevelProgress).where(
                                UserLevelProgress.user_id == user_id,
                                UserLevelProgress.level_id == next_level.id,
                            )
                        )
                    ).scalar_one_or_none()
                    if nlp and nlp.status == "locked":
                        nlp.status = "available"
            else:
                # Level 10 complete → psychometric checkpoint
                next_action = "psychometric_checkpoint"
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
    await db.commit()
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
    if upp:
        upp.status = "completed"
        upp.completed_at = datetime.now(timezone.utc)

    phase = (await db.execute(select(Phase).where(Phase.id == phase_id))).scalar_one_or_none()
    if not phase:
        return
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
