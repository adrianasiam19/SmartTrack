import random
from typing import List, Optional, Dict, Set
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from datetime import datetime, timezone
import uuid

from app.assessment.models import (
    Question, UserSkillEstimate, Response, BehavioralProfile, Leaderboard,
    LearningModule, PsychometricCard, PsychometricResponse
)
from app.assessment.schemas import (
    AssessmentListResponse, QuestionResponse, TelemetrySubmitRequest,
    TelemetrySubmitResponse, CalibrationStartResponse, NextQuestionResponse,
    PsychometricCardResponse, PsychometricSubmitRequest, PsychometricSubmitResponse,
    DashboardResponse, LeaderboardResponse, LeaderboardEntry,
    SaveAcademicRecordsRequest, ConfirmAcademicUploadRequest,
    LearningModuleResponse, RecommendedModulesResponse,
    ExplanationRequest, ExplanationResponse, DashboardResponse,
    GenerateChallengeRequest, GenerateChallengeResponse, GeneratedChallenge,
    BehaviourSessionRequest, BehaviourSessionResponse,
)
from app.assessment.engine import (
    update_theta, get_domain_weights, analyze_behavior, get_initial_prior
)
from app.assessment.recommendation_engine import RecommendationEngine
from app.assessment.academic_recommendations import (
    validate_academic_file,
    save_academic_file,
    analyze_academic_document,
    compare_candidate_to_profile,
    merge_academic_upload_into_profile,
    merge_academic_pending_into_profile,
    clear_academic_pending_from_profile,
    clear_academic_upload_from_profile,
    delete_stored_academic_file,
    has_academic_upload,
    programme_fallback_skills,
    MIN_GRADES_FOR_CONFIRM,
)
from app.recommendations.ml_career import generate_ml_knust_alternate
from app.recommendations.eligibility import evaluate_recommendation_eligibility
from app.recommendations.messages import (
    AGGREGATE_UNAVAILABLE,
    GRADES_NOT_EXTRACTED,
    ML_FALLBACK_NOTICE,
    NO_ACADEMIC_UPLOAD,
    NO_MATCHING_PROGRAMMES,
    PHASE_INCOMPLETE,
)
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User, AcademicRecord
import base64
from app.assessment.ai_agent import get_ai_explanation
from app.assessment.deepseek_service import generate_challenge_question
from app.assessment.prefetch_manager import prefetch_manager
import logging

logger = logging.getLogger(__name__)

# Simple obfuscation secret
OBFUSCATION_SALT = "ST_SEC_2024"

def obfuscate_answer(answer: str) -> str:
    """Cheap encryption for local feedback speed."""
    return base64.b64encode(f"{OBFUSCATION_SALT}:{answer}".encode()).decode()

def serialize_question(q: Question) -> Dict:
    """Convert Question ORM to dict and add obfuscated hash."""
    resp = QuestionResponse.model_validate(q).model_dump()
    resp["answer_hash"] = obfuscate_answer(q.correct_answer)
    return resp


def serialize_ai_question(q: Dict) -> Dict:
    """Convert an AI-generated question dict into the same frontend-facing shape."""
    return {
        "id": q["id"],
        "domain": q["domain"],
        "question": q["question"],
        "options": q["options"],
        "answer_hash": obfuscate_answer(q["correct_answer"]),
    }

router = APIRouter(prefix="/challenges", tags=["Challenges"])


@router.get("/questions", response_model=AssessmentListResponse)
async def get_all_questions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all challenge questions (without answers for security)."""
    result = await db.execute(select(Question).order_by(Question.id))
    questions = result.scalars().all()

    return {
        "questions": [serialize_question(q) for q in questions],
        "total": len(questions),
    }


@router.get("/questions/{domain}", response_model=AssessmentListResponse)
async def get_questions_by_domain(
    domain: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get questions filtered by domain."""
    result = await db.execute(
        select(Question).where(Question.domain == domain).order_by(Question.id)
    )
    questions = result.scalars().all()

    return {
        "questions": [serialize_question(q) for q in questions],
        "total": len(questions),
    }


# ──────────────────────────────────────────────────────────────────────────────
# AI Challenge Generation
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/generate-challenge", response_model=GenerateChallengeResponse)
async def generate_challenge(
    body: GenerateChallengeRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Generate a dynamic SHS challenge question using AI (DeepSeek / NVIDIA).
    
    This endpoint allows the system to generate challenge questions on-the-fly
    instead of relying solely on hardcoded questions.
    
    Args:
        body: GenerateChallengeRequest with category, difficulty, programme, and optional concept
    
    Returns:
        GenerateChallengeResponse with generated challenge or error message
    """
    from app.security.rate_limit import rate_limit

    rate_limit(http_request, scope="ai-generate-challenge", limit=10, window_seconds=60)

    result = await generate_challenge_question(
        category=body.category,
        difficulty=body.difficulty,
        programme=body.programme,
        concept=body.concept,
    )
    
    if result["success"]:
        return GenerateChallengeResponse(
            success=True,
            data=GeneratedChallenge(**result["data"]),
            error=None,
        )
    else:
        return GenerateChallengeResponse(
            success=False,
            data=None,
            error=result.get("error", "Unknown error occurred"),
        )


# ──────────────────────────────────────────────────────────────────────────────
# Stealth Challenge Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/calibration/start", response_model=CalibrationStartResponse)
async def start_calibration(
    domain: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start placement matches (Calibration Phase).
    
    Builds a pre-shuffled pool of unique questions for the session.
    Questions are randomly selected across domains (or filtered by domain).
    """
    # Clear any previous session pool for this user
    user_id_str = str(current_user.id)
    _clear_session_pool(user_id_str)
    pool = _get_session_pool(user_id_str)
    
    # Fetch ALL questions (or filtered by domain)
    if domain:
        result = await db.execute(select(Question).where(Question.domain == domain))
    else:
        result = await db.execute(select(Question))
    questions = result.scalars().all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="No questions available.")
    
    # Build a shuffled pool of all questions
    shuffled = list(questions)
    random.shuffle(shuffled)
    pool["pool"] = shuffled
    pool["pool_idx"] = 0
    
    # Return first batch (10 for calibration)
    batch_size = 10
    selected = shuffled[:batch_size]
    pool["pool_idx"] = batch_size
    pool["used_ids"].update(q.id for q in selected)
    
    # ── Background prefetch AI questions while user plays ────
    programme = current_user.programme or current_user.category or "General Science"
    prefetch_manager.start_prefetch(
        user_id=user_id_str,
        programme=programme,
        count=5,
    )
    
    return {
        "questions": [serialize_question(q) for q in selected],
        "initial_theta": 0.0
    }


# ── In-memory session question pool ──────────────────────────────────────
# Tracks which question IDs have been served to each user session
_session_pools: Dict[str, Dict] = {}

def _get_session_pool(user_id: str) -> Dict:
    """Get or create a session pool for the user."""
    if user_id not in _session_pools:
        _session_pools[user_id] = {
            "used_ids": set(),         # question IDs already served
            "psychometric_shown": [],
        "psychometric_responses": [],  # psychometric answer history
            "pool": [],                # pre-shuffled question pool
            "pool_idx": 0,             # current index in the pool
        }
    return _session_pools[user_id]

def _clear_session_pool(user_id: str) -> None:
    _session_pools.pop(user_id, None)


async def _get_next_adaptive_questions(
    current_user: User,
    db: AsyncSession,
    domain: Optional[str] = None,
    limit: int = 5,
    include_prefetched: bool = True,
    exclude_ids: Optional[Set[int]] = None,
) -> List:
    """
    Pick unique questions for a user — never repeats within a session.
    
    Priority order:
    1. Prefetched AI questions (if any) — seamless swap-in
    2. Pre-shuffled session pool (avoids duplicates)
    3. Random sample from DB questions filtered by exclude_ids
    
    Returns a mix of Question ORM objects and AI question dicts.
    """
    user_id_str = str(current_user.id)
    
    # 1. Grab prefetched AI questions first
    prefetched = []
    if include_prefetched:
        prefetched = prefetch_manager.get_questions(user_id_str, limit=limit)
    
    needed = limit - len(prefetched)
    if needed <= 0:
        return prefetched[:limit]
    
    # 2. Try session pool first (pre-shuffled, deduped)
    pool = _get_session_pool(user_id_str)
    pool_questions = []
    if pool["pool"] and pool["pool_idx"] < len(pool["pool"]):
        remaining = pool["pool"][pool["pool_idx"]:pool["pool_idx"] + needed]
        pool_questions = remaining
        pool["pool_idx"] += len(remaining)
        needed -= len(pool_questions)
    
    # 3. Fill remaining from DB with proper dedup
    if needed > 0:
        # Build exclude set: already used + what we're returning now
        used = set(exclude_ids or [])
        used.update(pool["used_ids"])
        for q in pool_questions:
            used.add(q.id)
        
        weights = get_domain_weights(current_user.category or "")
        
        selected_domain = domain
        if not selected_domain:
            domains = list(weights.keys())
            probs = list(weights.values())
            selected_domain = random.choices(domains, weights=probs, k=1)[0]
        
        q_result = await db.execute(
            select(Question).where(Question.domain == selected_domain)
        )
        domain_questions = q_result.scalars().all()
        
        # Filter out used IDs
        available = [q for q in domain_questions if q.id not in used]
        
        if not available:
            # Fallback: any question from any domain, excluding used
            fallback_res = await db.execute(select(Question))
            all_qs = fallback_res.scalars().all()
            available = [q for q in all_qs if q.id not in used]
        
        if available:
            # Random sample instead of IRT-sorted
            sample_size = min(needed, len(available))
            random.shuffle(available)
            fresh = available[:sample_size]
            
            # Track these IDs
            pool["used_ids"].update(q.id for q in fresh)
            pool_questions.extend(fresh)
    
    # Merge: prefetched AI first, then DB questions
    result = list(prefetched)
    result.extend(pool_questions)
    return result[:limit]


@router.get("/question/next", response_model=NextQuestionResponse)
async def get_next_question(
    domain: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch the next batch of adaptive questions.
    
    Returns both DB and AI-prefetched questions. Frontend can poll this
    when its local queue runs low to avoid showing an empty state.
    Uses the session pool to avoid returning duplicates.
    """
    session_pool = _get_session_pool(str(current_user.id))
    selected = await _get_next_adaptive_questions(
        current_user, db, domain, limit=5,
        exclude_ids=session_pool["used_ids"],
    )
    serialized = []
    for q in selected:
        if isinstance(q, dict):
            serialized.append(serialize_ai_question(q))
        else:
            serialized.append(serialize_question(q))
    return {"questions": serialized}


# ── Psychometric Card Endpoints ──────────────────────────────────────────────

@router.get("/psychometric/card", response_model=PsychometricCardResponse)
async def get_psychometric_card(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return ONE random psychometric insight card, tracking which cards
    have been shown this session.
    
    Each call returns a different card until all have been seen.
    """
    import random
    
    result = await db.execute(select(PsychometricCard))
    all_cards = result.scalars().all()
    
    if not all_cards:
        # Fallback to static cards if DB is empty
        from app.assessment.psychometric_cards import PSYCHOMETRIC_CARDS
        pool = [c for c in PSYCHOMETRIC_CARDS if c.get("id")]
        if not pool:
            raise HTTPException(status_code=404, detail="No psychometric cards available.")
        
        chosen = random.choice(pool)
        # Flatten: remove trait_weights for frontend
        return {
            "id": chosen["id"],
            "category": chosen.get("category", "Insight"),
            "question": chosen["question"],
            "display": chosen.get("display", "choose"),
            "options": [
                {"value": o["value"], "label": o["label"]}
                for o in chosen["options"]
            ],
        }
    
    # Filter cards not yet shown this session
    pool = _get_session_pool(str(current_user.id))
    shown_ids = set(pool.get("psychometric_shown", []))
    available = [c for c in all_cards if c.card_id not in shown_ids]
    
    if not available:
        # All cards shown — reset and start fresh
        pool["psychometric_shown"] = []
        available = list(all_cards)
    
    chosen = random.choice(available)
    pool["psychometric_shown"].append(chosen.card_id)
    
    return {
        "id": chosen.card_id,
        "category": "Insight",
        "question": chosen.question,
        "display": "choose",
        "options": [
            {"value": o["value"], "label": o["label"]}
            for o in chosen.options
        ],
    }


@router.post("/psychometric", response_model=PsychometricSubmitResponse)
async def submit_psychometric_answer(
    body: PsychometricSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a user's response to a psychometric insight card."""
    response = PsychometricResponse(
        user_id=current_user.id,
        card_id=body.question_id,
        answer=body.answer,
    )
    db.add(response)
    await db.commit()
    return PsychometricSubmitResponse(
        success=True,
        message="Psychometric response recorded.",
    )


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch the student's cognitive profile and behavioral metrics."""
    # 1. Fetch Skill Estimates (Thetas)
    result = await db.execute(select(UserSkillEstimate).where(UserSkillEstimate.user_id == current_user.id))
    estimates = result.scalars().all()
    
    radar_chart = {est.domain: (est.theta + 4) / 8 for est in estimates} # Normalize [-4,4] to [0,1]
    
    # Fill missing domains with 0.5 (neutral)
    for domain in ["Math", "Logic", "Verbal", "Science", "General"]:
        if domain not in radar_chart:
            radar_chart[domain] = 0.5

    # 2. Analyze Behavioral Telemetry
    result = await db.execute(select(Response).where(Response.user_id == current_user.id))
    responses = result.scalars().all()
    behavioral_traits = analyze_behavior(responses)

    # 3. Calculate Overall Score (Percentile Proxy)
    avg_theta = sum(est.theta for est in estimates) / len(estimates) if estimates else 0
    overall_score = round(70 + (avg_theta * 10), 1) # Simple mapping to a 0-100 scale

    # 4. Generate Career Matches (Basic Logic)
    # Sort domains by strength
    sorted_domains = sorted(radar_chart.items(), key=lambda x: x[1], reverse=True)
    top_domain = sorted_domains[0][0]
    
    matches = []
    if top_domain == "Math":
        matches = [{"path": "Data Science", "match": 0.95}, {"path": "Engineering", "match": 0.92}]
    elif top_domain == "Logic":
        matches = [{"path": "Software Development", "match": 0.98}, {"path": "Philosophy", "match": 0.85}]
    elif top_domain == "Verbal":
        matches = [{"path": "Law", "match": 0.94}, {"path": "Journalism", "match": 0.90}]
    else:
        matches = [{"path": "Project Management", "match": 0.88}, {"path": "Consulting", "match": 0.82}]

    return {
        "radar_chart": radar_chart,
        "behavioral_traits": behavioral_traits,
        "overall_score": overall_score,
        "career_matches": matches
    }


@router.post("/explain", response_model=ExplanationResponse)
async def get_explanation(
    request: ExplanationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get an AI-generated explanation for a question."""
    q = await db.get(Question, request.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
        
    explanation = await get_ai_explanation(
        question_text=q.question,
        selected_option=request.selected_option,
        correct_option=q.correct_answer,
        options=q.options
    )
    
    return {"explanation": explanation}


@router.post("/response/submit", response_model=TelemetrySubmitResponse)
async def submit_response(
    body: TelemetrySubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Process an answer, update IRT theta, and analyze behavioral telemetry."""
    try:
        is_correct = False
        domain = "General"
        difficulty_b = 0.0
        difficulty_a = 1.2
        difficulty_c = 0.25
        question_id = body.question_id

        # ── AI-generated questions (negative IDs) ────────────────────────
        # These don't exist in DB, so we skip the DB question fetch for them.
        # IRT update is also skipped since we don't have difficulty params.
        if question_id > 0:
            result = await db.execute(
                select(Question).where(Question.id == question_id)
            )
            question = result.scalar_one_or_none()
            if not question:
                raise HTTPException(status_code=404, detail="Question not found.")

            is_correct = (body.selected_option == question.correct_answer)
            domain = question.domain
            difficulty_a = question.difficulty_a
            difficulty_b = question.difficulty_b
            difficulty_c = question.difficulty_c
            question_id = question.id

        else:
            # AI question — trust frontend-computed correctness, skip IRT update
            is_correct = body.is_correct if body.is_correct is not None else True

        # 2. Record Telemetry Response
        response = Response(
            user_id=current_user.id,
            question_id=question_id,
            correct=is_correct,
            time_taken_seconds=body.time_taken_seconds,
            hints_used=body.hints_used
        )
        db.add(response)

        # 3. Update IRT Theta (only for DB questions)
        if body.question_id > 0:
            skill_result = await db.execute(
                select(UserSkillEstimate)
                .where(UserSkillEstimate.user_id == current_user.id)
                .where(UserSkillEstimate.domain == domain)
            )
            skill = skill_result.scalar_one_or_none()

            if not skill:
                initial_theta = get_initial_prior(current_user.category, domain)
                skill = UserSkillEstimate(
                    user_id=current_user.id, domain=domain, theta=initial_theta
                )
                db.add(skill)

            new_theta = update_theta(
                theta=skill.theta,
                correct=is_correct,
                a=difficulty_a,
                b=difficulty_b,
                c=difficulty_c,
            )
            skill.theta = new_theta
            skill.last_updated = datetime.now(timezone.utc)

        # 4. Behavioral Analysis
        responses_res = await db.execute(
            select(Response).where(Response.user_id == current_user.id)
            .order_by(desc(Response.timestamp)).limit(50)
        )
        recent_responses = responses_res.scalars().all()

        traits = analyze_behavior(recent_responses)

        # Save traits
        for trait_name, value in traits.items():
            trait_res = await db.execute(
                select(BehavioralProfile)
                .where(BehavioralProfile.user_id == current_user.id)
                .where(BehavioralProfile.trait == trait_name)
            )
            profile = trait_res.scalar_one_or_none()
            if not profile:
                profile = BehavioralProfile(
                    user_id=current_user.id, trait=trait_name
                )
                db.add(profile)
            profile.value = value
            profile.last_updated = datetime.now(timezone.utc)

        # Arena / legacy challenge answers also count toward daily streak.
        from app.users.gamification import record_daily_challenge_streak

        streak_info = record_daily_challenge_streak(current_user)

        await db.commit()

        # 5. Get Next Batch from session pool (no repeats)
        session_pool = _get_session_pool(str(current_user.id))
        next_qs = await _get_next_adaptive_questions(
            current_user, db, domain, limit=3,
            exclude_ids=session_pool["used_ids"],
        )
        next_qs_resp = []
        for q in next_qs:
            if isinstance(q, dict):
                next_qs_resp.append(serialize_ai_question(q))
            else:
                next_qs_resp.append(serialize_question(q))

        return {
            "status": "success",
            "is_correct": is_correct,
            "next_questions": next_qs_resp,
            "streak": streak_info.get("streak"),
            "streak_updated": streak_info.get("incremented"),
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/behaviour", response_model=BehaviourSessionResponse)
async def submit_behaviour_session(
    body: BehaviourSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Persist session-level behavioural signals from competitive arenas.

    Complements per-answer /response/submit analysis with an end-of-session summary
    (retries, pace, consistency) used by recommendation soft signals.
    """
    answered = max(0, int(body.questions_answered or 0))
    correct = max(0, int(body.correct_answers or 0))
    accuracy = (correct / answered) if answered else 0.0
    avg_time = float(body.response_time_avg or 0.0)
    if avg_time <= 0 and body.response_times:
        avg_time = sum(body.response_times) / len(body.response_times)

    # Normalize to 0–1 trait scale used by BehavioralProfile / recommendations.
    persistence = min(1.0, (body.retries / 5.0) + (avg_time / 60.0) * 0.5)
    processing_speed = min(1.0, 30.0 / max(1.0, avg_time)) if accuracy >= 0.4 else 0.0
    carefulness = min(1.0, accuracy * min(1.0, avg_time / 20.0))
    consistency = min(1.0, max(0.0, float(body.consistency or 0.0) / 100.0))

    traits = {
        "Persistence": round(persistence, 4),
        "Processing Speed": round(processing_speed, 4),
        "Carefulness": round(carefulness, 4),
        "Consistency": round(consistency, 4),
    }
    if body.domain:
        # Trait column is String(50) — keep keys short.
        domain_key = f"Pref:{body.domain}"[:50]
        traits[domain_key] = 1.0

    now = datetime.now(timezone.utc)
    for trait_name, value in traits.items():
        trait_res = await db.execute(
            select(BehavioralProfile)
            .where(BehavioralProfile.user_id == current_user.id)
            .where(BehavioralProfile.trait == trait_name)
        )
        profile = trait_res.scalar_one_or_none()
        if not profile:
            profile = BehavioralProfile(user_id=current_user.id, trait=trait_name)
            db.add(profile)
        # Blend with prior value so one noisy session doesn't overwrite history.
        prior = float(profile.value or 0.0) if profile.value is not None else value
        profile.value = round((prior * 0.6) + (value * 0.4), 4)
        profile.last_updated = now

    await db.commit()
    return BehaviourSessionResponse(status="success", traits=traits)


@router.get("/leaderboard/{domain}/{category}", response_model=LeaderboardResponse)
async def get_leaderboard(
    domain: str,
    category: str,
    db: AsyncSession = Depends(get_db)
):
    """Segmented leaderboards."""
    # Simplified: fetch top users from Leaderboard table
    query = select(Leaderboard, User).join(User, Leaderboard.user_id == User.id).where(Leaderboard.domain == domain)
    if category != "Global":
        query = query.where(Leaderboard.category == category)
        
    query = query.order_by(desc(Leaderboard.score)).limit(10)
    
    result = await db.execute(query)
    rows = result.all()
    
    entries = []
    for rank, (lb, user) in enumerate(rows, 1):
        entries.append({
            "user_name": user.full_name,
            "score": lb.score,
            "rank": rank
        })

    return {
        "domain": domain,
        "category": category,
        "entries": entries
    }


@router.get("/recommendations/generate", response_model=dict)
async def generate_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Dual-path programme recommendations.

    • Without WASSCE: BehaviouralProgrammeMatch from psych + challenges + learning.
    • With WASSCE: admission refine (aggregate + cut-offs + Decision Tree) that
      tweaks the behavioural picture with academic results.

    Requires all levels completed in at least one phase. WASSCE is never mandatory.
    """
    from app.config import settings as app_settings
    from app.recommendations.service import generate_behavioural_recommendations

    debug_mode = bool(getattr(app_settings, "RECOMMENDATION_DEBUG", False))

    eligibility = await evaluate_recommendation_eligibility(db, current_user)
    if not eligibility.get("eligible"):
        detail = dict(PHASE_INCOMPLETE)
        detail["title"] = eligibility.get("title") or detail["title"]
        detail["message"] = eligibility.get("message") or detail["message"]
        detail["short_message"] = eligibility.get("short_message") or detail["short_message"]
        detail["eligibility"] = eligibility
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    skills_res = await db.execute(
        select(UserSkillEstimate).where(UserSkillEstimate.user_id == current_user.id)
    )
    skills = skills_res.scalars().all()
    skill_estimates = {skill.domain: skill.theta for skill in skills}

    traits_res = await db.execute(
        select(BehavioralProfile).where(BehavioralProfile.user_id == current_user.id)
    )
    traits = traits_res.scalars().all()
    behavioral_traits = {trait.trait: trait.value for trait in traits}

    grades_res = await db.execute(
        select(AcademicRecord).where(AcademicRecord.user_id == current_user.id)
    )
    grade_rows = grades_res.scalars().all()
    academic_grades = [
        {"subject": row.subject, "grade": row.grade} for row in grade_rows
    ]

    profile = current_user.learner_profile if isinstance(current_user.learner_profile, dict) else {}
    upload = profile.get("academic_upload") or {}
    if (
        not academic_grades
        and isinstance(upload, dict)
        and upload.get("confirmed") is not False
        and isinstance(upload.get("grades"), list)
    ):
        academic_grades = [
            {"subject": g.get("subject", ""), "grade": g.get("grade", "")}
            for g in upload["grades"]
            if g.get("subject") and g.get("grade")
        ]

    # ── Path A: behavioural match (no WASSCE) ───────────────────────────────
    if not academic_grades:
        behavioural = await generate_behavioural_recommendations(
            db, current_user, limit=8
        )
        programmes = list(behavioural.get("programmes") or [])
        if not programmes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=NO_MATCHING_PROGRAMMES,
            )
        # Number ranks explicitly for UI (order = strength; no percentages).
        for i, card in enumerate(programmes, start=1):
            card["rank"] = card.get("rank") or i

        refine_hint = None
        if eligibility.get("all_phases_completed"):
            refine_hint = (
                "Optional: upload your WASSCE or academic results to refine these "
                "matches with aggregate and admission cut-offs."
            )
        elif eligibility.get("wassce_recommended_now"):
            refine_hint = (
                "When you finish all phases, you can upload WASSCE results to tweak "
                "this list with admission insights."
            )

        payload: dict = {
            "success": True,
            "recommendation_kind": "behavioural_match",
            "wassce_used": False,
            "academic_score": None,
            "performance_level": None,
            "summary_message": behavioural.get("summary_message"),
            "detailed_message": (
                "These programmes are ranked from your psychometric profile, challenge "
                "performance, and learning activity in Atlas. Order shows match strength. "
                "WASSCE upload is optional and refines admission insights later."
            ),
            "recommendations": programmes,
            "suitable_programmes": programmes,
            "competitive_programmes": [],
            "grades_used": 0,
            "admission_insights": None,
            "knust": None,
            "source": "behavioural_match",
            "primary_source": "behavioural_match",
            "used_fallback": False,
            "learner_notice": refine_hint,
            "ml_alternate": None,
            "upload": {
                "filename": upload.get("filename"),
                "grades_extracted": bool(upload.get("grades_extracted")),
            },
            "eligibility": eligibility,
        }
        if debug_mode:
            payload["debug"] = {
                "recommendation_kind": "behavioural_match",
                "family_fit_scores": behavioural.get("family_fit_scores"),
                "confidence": behavioural.get("confidence"),
                "signals": behavioural.get("signals"),
                "skill_domains": list(skill_estimates.keys()),
                "trait_keys": list(behavioral_traits.keys()),
            }
        try:
            from app.notifications.events import notify_recommendations_unlocked

            await notify_recommendations_unlocked(db, current_user.id)
            await db.commit()
        except Exception:
            logger.exception("Failed to create recommendations-unlocked notification")
        return payload

    # ── Path B: WASSCE refine (admission + DT) ───────────────────────────────
    if not skill_estimates:
        skill_estimates = programme_fallback_skills(current_user.programme)

    # Behavioural baseline kept for comparison / messaging (same cumulative signals).
    behavioural = await generate_behavioural_recommendations(db, current_user, limit=8)
    behavioural_names = [
        str(p.get("programme")) for p in (behavioural.get("programmes") or [])[:8]
    ]

    engine = RecommendationEngine(
        skill_estimates=skill_estimates,
        behavioral_traits=behavioral_traits,
        academic_grades=academic_grades,
        programme=current_user.programme,
        learner_profile=profile,
    )
    recommendations_result = engine.generate_recommendations()

    if recommendations_result.get("error") == "aggregate_unavailable":
        # Soft-fall back to behavioural matches (same as empty cut-off path) —
        # partial/odd uploads must not hard-block recommendations.
        suitable = list(behavioural.get("programmes") or [])
        if not suitable:
            detail = dict(AGGREGATE_UNAVAILABLE)
            if recommendations_result.get("summary_message"):
                detail["message"] = (
                    f"{detail['message']}\n\nDetails: {recommendations_result['summary_message']}"
                )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        for i, card in enumerate(suitable, start=1):
            if isinstance(card, dict):
                card["rank"] = card.get("rank") or i
        notice = (
            "Atlas could not compute an admission aggregate from this upload, "
            "so your behavioural programme matches were kept. Re-upload clearer "
            "results anytime to refine with cut-offs."
        )
        if recommendations_result.get("summary_message"):
            notice = f"{notice} ({recommendations_result['summary_message']})"
        payload = {
            "success": True,
            "recommendation_kind": "behavioural_match",
            "wassce_used": True,
            "academic_score": None,
            "performance_level": None,
            "summary_message": behavioural.get("summary_message"),
            "detailed_message": (
                "Your long-term Atlas behaviour still drives these ranked matches. "
                "Admission refine needs a complete aggregate from uploaded grades."
            ),
            "recommendations": suitable,
            "suitable_programmes": suitable,
            "competitive_programmes": [],
            "grades_used": recommendations_result.get("grades_used", 0),
            "admission_insights": None,
            "knust": None,
            "source": "behavioural_match_after_grades",
            "primary_source": "behavioural_match_after_grades",
            "used_fallback": True,
            "learner_notice": notice,
            "behavioural_baseline": behavioural_names,
            "ml_alternate": None,
            "upload": {
                "filename": upload.get("filename"),
                "grades_extracted": bool(upload.get("grades_extracted")),
            },
            "eligibility": eligibility,
        }
        try:
            from app.notifications.events import notify_recommendations_unlocked

            await notify_recommendations_unlocked(db, current_user.id)
            await db.commit()
        except Exception:
            logger.exception("Failed to create recommendations-unlocked notification")
        return payload

    ml_primary = generate_ml_knust_alternate(
        academic_grades=academic_grades,
        behavioral_traits=behavioral_traits,
        skill_estimates=skill_estimates,
        xp=int(getattr(current_user, "xp", 0) or 0),
        streak_days=int(getattr(current_user, "streak", 0) or 0),
        knust_payload=recommendations_result.get("knust"),
    )

    rules_suitable = recommendations_result.get("suitable_programmes") or []
    rules_competitive = recommendations_result.get("competitive_programmes") or []
    ml_programmes = (
        ml_primary.get("programmes") if ml_primary.get("enabled") else None
    ) or []

    learner_notice = (
        "Your WASSCE / academic results were used to refine the behavioural matches "
        "Atlas already built from your learning journey."
    )
    used_fallback = False

    if ml_programmes:
        suitable = ml_programmes
        primary_source = "knust_dt"
        summary = (
            "Atlas combined your behavioural profile with your uploaded results. "
            + (recommendations_result.get("summary_message") or "")
        ).strip()
    else:
        used_fallback = True
        suitable = rules_suitable
        primary_source = "atlas_cutoffs_fallback"
        summary = recommendations_result.get("summary_message")
        if ml_primary.get("error"):
            logger.error(
                "Decision Tree unavailable for user=%s error=%s detail=%s",
                current_user.id,
                ml_primary.get("error"),
                ml_primary.get("error_detail"),
            )
            learner_notice = ML_FALLBACK_NOTICE
        if not suitable and not rules_competitive:
            # Soft fall back to behavioural list rather than hard-fail after upload.
            suitable = list(behavioural.get("programmes") or [])
            primary_source = "behavioural_match_after_grades"
            summary = behavioural.get("summary_message")
            learner_notice = (
                "Admission cut-offs could not rank programmes for these grades, "
                "so Atlas kept your behavioural matches."
            )
            if not suitable:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=NO_MATCHING_PROGRAMMES,
                )

    for i, card in enumerate(suitable, start=1):
        if isinstance(card, dict):
            card["rank"] = card.get("rank") or i

    payload = {
        "success": True,
        "recommendation_kind": "wassce_refined",
        "wassce_used": True,
        "academic_score": recommendations_result.get("academic_score"),
        "performance_level": recommendations_result.get("performance_level"),
        "summary_message": summary,
        "detailed_message": (
            "Recommendations combine your long-term Atlas behaviour with uploaded "
            "academic results, aggregate, and admission cut-offs. Order shows strength."
        ),
        "recommendations": suitable,
        "suitable_programmes": suitable,
        "competitive_programmes": rules_competitive,
        "grades_used": recommendations_result.get("grades_used", 0),
        "admission_insights": recommendations_result.get("admission_insights"),
        "knust": recommendations_result.get("knust"),
        "source": primary_source,
        "primary_source": primary_source,
        "used_fallback": used_fallback,
        "learner_notice": learner_notice,
        "behavioural_baseline": behavioural_names,
        "ml_alternate": None,
        "upload": {
            "filename": upload.get("filename"),
            "grades_extracted": bool(upload.get("grades_extracted")),
        },
        "eligibility": eligibility,
    }

    if debug_mode:
        predictions = ml_primary.get("predictions") or []
        payload["debug"] = {
            "recommendation_kind": "wassce_refined",
            "decision_tree_model_loaded": bool(ml_primary.get("model_loaded")),
            "recommendations_from_ml": primary_source == "knust_dt",
            "fallback_used": used_fallback,
            "primary_source": primary_source,
            "ml_error": ml_primary.get("error"),
            "ml_error_detail": ml_primary.get("error_detail"),
            "model_status": ml_primary.get("model_status"),
            "features_used": ml_primary.get("features_used") or {},
            "behavioural_baseline": behavioural_names,
            "prediction_confidence": [
                {
                    "programme": p.get("programme"),
                    "confidence": p.get("confidence"),
                    "eligibility_band": p.get("eligibility_band"),
                }
                for p in predictions[:12]
            ],
            "programme_count_ml": len(ml_programmes),
            "programme_count_fallback_suitable": len(rules_suitable),
            "grades_count": len(academic_grades),
            "skill_domains": list(skill_estimates.keys()),
            "trait_keys": list(behavioral_traits.keys()),
        }

    try:
        from app.notifications.events import notify_recommendations_unlocked

        await notify_recommendations_unlocked(db, current_user.id)
        await db.commit()
    except Exception:
        logger.exception("Failed to create recommendations-unlocked notification")

    return payload


def _academic_error(code: str, title: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"code": code, "title": title, "message": message},
    )


@router.post("/academic/upload")
async def upload_academic_results(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a WASSCE results file for preview.

    Does NOT save grades until the learner confirms via /academic/confirm.
    Rejects files that do not look like WAEC/WASSCE results.
    """
    data = await file.read()
    filename = file.filename or "academic_results.pdf"
    error = validate_academic_file(filename, file.content_type, len(data))
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    analysis = await analyze_academic_document(
        filename=filename,
        content_type=file.content_type,
        data=data,
        profile_name=getattr(current_user, "full_name", None),
    )
    grades = list(analysis.get("grades") or [])
    waec = analysis.get("waec") or {}
    is_waec = bool(waec.get("is_waec"))
    name_match = analysis.get("name_match") or {}
    candidate_name = analysis.get("candidate_name")

    if not is_waec:
        reasons = list(waec.get("reasons") or [])
        if "no_readable_text" in reasons or "unreadable" in reasons:
            raise _academic_error(
                "wassce_unreadable",
                "Could not read this file",
                "Atlas could not read text from this PDF (it may be a scan or image-only file). "
                "Please upload a clearer photo of your WASSCE results slip, or a text-based PDF export.",
            )
        raise _academic_error(
            "not_waec_document",
            "This doesn't look like a WAEC results document",
            "Atlas only accepts WAEC/WASSCE results slips (or a clear photo/PDF of one). "
            "School reports, transcripts, and other documents are not accepted. "
            "Please upload your official WASSCE statement of results.",
        )

    if name_match.get("reason") == "profile_name_incomplete":
        raise _academic_error(
            "profile_name_incomplete",
            "Complete your profile name first",
            "Your Atlas profile needs your full name (at least first and last name) "
            "so we can match it to the candidate name on your WASSCE results. "
            "Update your profile, then upload again.",
        )

    if name_match.get("reason") == "document_name_missing" or not candidate_name:
        raise _academic_error(
            "candidate_name_missing",
            "Could not read the candidate name",
            "Atlas could not find a candidate name on this results document. "
            "Please upload a clearer full-page copy of your WASSCE statement of results "
            "where your name is visible.",
        )

    if not name_match.get("matched"):
        doc = name_match.get("document_name") or candidate_name or "unknown"
        profile = name_match.get("profile_name") or current_user.full_name or "your profile"
        raise _academic_error(
            "name_mismatch",
            "Name on results does not match your profile",
            f"The candidate name on this document (“{doc}”) does not match your Atlas "
            f"profile name (“{profile}”). "
            "You can only upload your own WASSCE results. "
            "If your profile name is wrong, update it to match your results slip, then try again.",
        )

    if len(grades) < MIN_GRADES_FOR_CONFIRM:
        raise _academic_error(
            "wassce_extraction_failed",
            "WASSCE results could not be extracted",
            "We recognised a WAEC-style document but could not read enough subject grades "
            f"(need at least {MIN_GRADES_FOR_CONFIRM}). "
            "Please re-upload a clearer PDF or image of the full results page.",
        )

    stored_name, _path = save_academic_file(str(current_user.id), filename, data)
    profile = (
        current_user.learner_profile
        if isinstance(current_user.learner_profile, dict)
        else {}
    )
    # Drop any previous pending file before storing a new preview.
    old_pending = profile.get("academic_upload_pending") or {}
    if isinstance(old_pending, dict):
        delete_stored_academic_file(
            str(current_user.id), old_pending.get("stored_name")
        )

    current_user.learner_profile = merge_academic_pending_into_profile(
        profile,
        filename=filename,
        stored_name=stored_name,
        grades=grades,
        waec=waec,
        candidate_name=candidate_name,
        name_match=name_match,
    )
    await db.commit()
    await db.refresh(current_user)

    return {
        "success": True,
        "needs_confirmation": True,
        "filename": filename,
        "stored_name": stored_name,
        "grades_extracted": True,
        "records": grades,
        "candidate_name": candidate_name,
        "name_match": name_match,
        "waec": waec,
        "message": (
            f"Name matched (“{candidate_name}”). Found {len(grades)} subject grade(s). "
            "Please confirm these grades before Atlas uses them."
        ),
        "code": None,
        "title": None,
    }


@router.post("/academic/confirm")
async def confirm_academic_upload(
    body: ConfirmAcademicUploadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Persist confirmed WASSCE grades after the learner reviews the extraction."""
    if not body.records:
        raise _academic_error(
            "no_grades",
            "No grades to confirm",
            "Confirm at least one subject grade, or cancel and upload again.",
        )

    profile = (
        current_user.learner_profile
        if isinstance(current_user.learner_profile, dict)
        else {}
    )
    pending = profile.get("academic_upload_pending") or {}
    filename = body.filename or pending.get("filename") or "wassce_results.pdf"
    stored_name = body.stored_name or pending.get("stored_name") or "confirmed"

    # Re-check name against the slip name captured at upload (blocks profile spoofing
    # after a successful upload of someone else's results).
    pending_candidate = None
    if isinstance(pending, dict):
        pending_candidate = pending.get("candidate_name")
    name_check = compare_candidate_to_profile(
        getattr(current_user, "full_name", None),
        pending_candidate,
    )
    if not name_check.get("matched"):
        raise _academic_error(
            "name_mismatch",
            "Name on results does not match your profile",
            "These results cannot be confirmed because the candidate name on the document "
            "does not match your Atlas profile name. Upload your own WASSCE results, "
            "or update your profile name to match your slip.",
        )

    grade_list = [
        {"subject": r.subject.strip(), "grade": r.grade.strip().upper()}
        for r in body.records
        if r.subject and r.grade
    ]
    if len(grade_list) < 1:
        raise _academic_error(
            "no_grades",
            "No grades to confirm",
            "Confirm at least one subject grade, or cancel and upload again.",
        )

    # Replace previous confirmed file on disk when confirming a new pending upload.
    old_upload = profile.get("academic_upload") or {}
    if isinstance(old_upload, dict):
        old_stored = old_upload.get("stored_name")
        if old_stored and old_stored != stored_name:
            delete_stored_academic_file(str(current_user.id), old_stored)

    await db.execute(
        delete(AcademicRecord).where(AcademicRecord.user_id == current_user.id)
    )
    for row in grade_list:
        db.add(
            AcademicRecord(
                user_id=current_user.id,
                subject=row["subject"],
                grade=row["grade"],
                exam_type=body.exam_type or "WASSCE",
            )
        )

    current_user.learner_profile = merge_academic_upload_into_profile(
        profile,
        filename=filename,
        stored_name=stored_name,
        grades=grade_list,
        confirmed=True,
    )
    await db.commit()
    await db.refresh(current_user)

    return {
        "success": True,
        "confirmed": True,
        "filename": filename,
        "records": grade_list,
        "message": f"Saved {len(grade_list)} WASSCE grade(s). Tap Get Recommendations to refine.",
    }


@router.delete("/academic/pending")
async def discard_academic_pending(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an unconfirmed upload preview without removing saved results."""
    profile = (
        current_user.learner_profile
        if isinstance(current_user.learner_profile, dict)
        else {}
    )
    pending = profile.get("academic_upload_pending") or {}
    if isinstance(pending, dict):
        delete_stored_academic_file(str(current_user.id), pending.get("stored_name"))
    current_user.learner_profile = clear_academic_pending_from_profile(profile)
    await db.commit()
    return {"success": True, "message": "Pending WASSCE upload discarded."}


@router.delete("/academic")
async def remove_academic_results(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove confirmed WASSCE grades and any pending upload."""
    profile = (
        current_user.learner_profile
        if isinstance(current_user.learner_profile, dict)
        else {}
    )
    for key in ("academic_upload", "academic_upload_pending"):
        block = profile.get(key) or {}
        if isinstance(block, dict):
            delete_stored_academic_file(str(current_user.id), block.get("stored_name"))

    await db.execute(
        delete(AcademicRecord).where(AcademicRecord.user_id == current_user.id)
    )
    current_user.learner_profile = clear_academic_upload_from_profile(profile)
    await db.commit()
    await db.refresh(current_user)

    return {
        "success": True,
        "message": "WASSCE results removed. Recommendations will use Atlas activity only.",
    }


@router.post("/academic/input")
async def save_academic_records(
    body: SaveAcademicRecordsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save user's WASSCE/academic grades for improved recommendation accuracy."""
    records: list[dict] = []
    if body.records:
        records = [
            {
                "subject": r.subject,
                "grade": r.grade,
                "exam_type": r.exam_type or body.exam_type,
            }
            for r in body.records
        ]
    elif body.results:
        records = [
            {"subject": subject, "grade": grade, "exam_type": body.exam_type}
            for subject, grade in body.results.items()
        ]

    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one academic grade.",
        )

    await db.execute(
        delete(AcademicRecord).where(AcademicRecord.user_id == current_user.id)
    )

    for record in records:
        db.add(
            AcademicRecord(
                user_id=current_user.id,
                subject=record["subject"],
                grade=record["grade"],
                exam_type=record.get("exam_type") or body.exam_type or "WASSCE",
            )
        )

    # Mark upload unlocked even for manual grade entry
    grade_list = [{"subject": r["subject"], "grade": r["grade"]} for r in records]
    current_user.learner_profile = merge_academic_upload_into_profile(
        current_user.learner_profile if isinstance(current_user.learner_profile, dict) else {},
        filename="manual_entry",
        stored_name="manual_entry",
        grades=grade_list,
        confirmed=True,
    )

    await db.commit()

    return {"success": True, "message": f"Saved {len(records)} academic records."}


# ──────────────────────────────────────────────────────────────────────────────
# Phase 3: Learning Module Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/learning/modules/recommended", response_model=RecommendedModulesResponse)
async def get_recommended_modules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return 3 learning modules that best match the user's current IRT skill level."""
    # Fetch user's current domain thetas
    skills_res = await db.execute(
        select(UserSkillEstimate).where(UserSkillEstimate.user_id == current_user.id)
    )
    skills = skills_res.scalars().all()
    user_theta: dict = {s.domain: s.theta for s in skills}

    # Get domain weights based on user category
    weights = get_domain_weights(current_user.category)

    # Fetch all modules
    mods_res = await db.execute(select(LearningModule))
    all_modules = mods_res.scalars().all()

    if not all_modules:
        return {"modules": [], "user_theta": user_theta}

    # Score each module: lower = closer to user's ability in that domain.
    # Also factor in category domain weights so relevant domains appear first.
    def module_score(mod: LearningModule) -> float:
        theta = user_theta.get(mod.domain, 0.0)
        domain_weight = weights.get(mod.domain, 0.1)
        ability_gap = abs(mod.difficulty_level - theta)
        # Modules that are slightly above the user's level are ideal (+0.5 offset)
        ideal_gap = abs(mod.difficulty_level - (theta + 0.5))
        return ideal_gap / (domain_weight + 0.01)  # favour category domains

    ranked = sorted(all_modules, key=module_score)
    top_3 = ranked[:3]

    return {
        "modules": [LearningModuleResponse.from_orm(m) for m in top_3],
        "user_theta": user_theta,
    }
