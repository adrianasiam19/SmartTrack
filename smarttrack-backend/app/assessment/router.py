import random
from typing import List, Optional, Dict, Set
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
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
    SaveAcademicRecordsRequest, LearningModuleResponse, RecommendedModulesResponse,
    ExplanationRequest, ExplanationResponse, DashboardResponse,
    GenerateChallengeRequest, GenerateChallengeResponse, GeneratedChallenge
)
from app.assessment.engine import (
    update_theta, get_domain_weights, analyze_behavior, get_initial_prior
)
from app.assessment.recommendation_engine import RecommendationEngine
from app.assessment.academic_recommendations import (
    validate_academic_file,
    save_academic_file,
    extract_grades_with_ai,
    merge_academic_upload_into_profile,
    has_academic_upload,
    programme_fallback_skills,
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
async def get_all_questions(db: AsyncSession = Depends(get_db)):
    """Get all challenge questions (without answers for security)."""
    result = await db.execute(select(Question).order_by(Question.id))
    questions = result.scalars().all()

    return {
        "questions": [serialize_question(q) for q in questions],
        "total": len(questions),
    }


@router.get("/questions/{domain}", response_model=AssessmentListResponse)
async def get_questions_by_domain(domain: str, db: AsyncSession = Depends(get_db)):
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
    request: GenerateChallengeRequest,
):
    """
    Generate a dynamic SHS challenge question using AI (DeepSeek / NVIDIA).
    
    This endpoint allows the system to generate challenge questions on-the-fly
    instead of relying solely on hardcoded questions.
    
    Args:
        request: GenerateChallengeRequest with category, difficulty, programme, and optional concept
    
    Returns:
        GenerateChallengeResponse with generated challenge or error message
    """
    result = await generate_challenge_question(
        category=request.category,
        difficulty=request.difficulty,
        programme=request.programme,
        concept=request.concept,
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
    Generate programme recommendations after academic upload unlock.

    Combines stealth challenge thetas (when available), behavioural traits,
    Starter Arena profile, declared programme, and uploaded academic grades.

    Requires all levels completed in at least one phase (Learning Center is
    encouraged but not mandatory).
    """
    from app.config import settings as app_settings

    debug_mode = bool(getattr(app_settings, "RECOMMENDATION_DEBUG", False))

    eligibility = await evaluate_recommendation_eligibility(db, current_user)
    if not eligibility.get("eligible"):
        detail = dict(PHASE_INCOMPLETE)
        detail["title"] = eligibility.get("title") or detail["title"]
        detail["message"] = eligibility.get("message") or detail["message"]
        detail["short_message"] = eligibility.get("short_message") or detail["short_message"]
        detail["eligibility"] = eligibility
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    if not has_academic_upload(current_user):
        existing = await db.execute(
            select(AcademicRecord).where(AcademicRecord.user_id == current_user.id).limit(1)
        )
        if existing.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=NO_ACADEMIC_UPLOAD,
            )

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
    if not academic_grades and isinstance(upload.get("grades"), list):
        academic_grades = [
            {"subject": g.get("subject", ""), "grade": g.get("grade", "")}
            for g in upload["grades"]
            if g.get("subject") and g.get("grade")
        ]

    if not academic_grades:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=GRADES_NOT_EXTRACTED,
        )

    if not skill_estimates:
        skill_estimates = programme_fallback_skills(current_user.programme)

    engine = RecommendationEngine(
        skill_estimates=skill_estimates,
        behavioral_traits=behavioral_traits,
        academic_grades=academic_grades,
        programme=current_user.programme,
        learner_profile=profile,
    )
    recommendations_result = engine.generate_recommendations()

    if recommendations_result.get("error") == "aggregate_unavailable":
        detail = dict(AGGREGATE_UNAVAILABLE)
        if recommendations_result.get("summary_message"):
            detail["message"] = (
                f"{detail['message']}\n\nDetails: {recommendations_result['summary_message']}"
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

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

    learner_notice = None
    used_fallback = False

    if ml_programmes:
        suitable = ml_programmes
        primary_source = "knust_dt"
        summary = (
            recommendations_result.get("summary_message")
            or "Here are programme matches based on your Atlas profile and results."
        )
    else:
        # Explicit cut-off fallback after logging (already done inside ml_career)
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=NO_MATCHING_PROGRAMMES,
            )

    payload: dict = {
        "success": True,
        "academic_score": recommendations_result.get("academic_score"),
        "performance_level": recommendations_result.get("performance_level"),
        "summary_message": summary,
        "detailed_message": recommendations_result.get("detailed_message"),
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
        "ml_alternate": None,
        "upload": {
            "filename": upload.get("filename"),
            "grades_extracted": bool(upload.get("grades_extracted")),
        },
    }

    if debug_mode:
        predictions = ml_primary.get("predictions") or []
        payload["debug"] = {
            "decision_tree_model_loaded": bool(ml_primary.get("model_loaded")),
            "recommendations_from_ml": primary_source == "knust_dt",
            "fallback_used": used_fallback,
            "primary_source": primary_source,
            "ml_error": ml_primary.get("error"),
            "ml_error_detail": ml_primary.get("error_detail"),
            "model_status": ml_primary.get("model_status"),
            "features_used": ml_primary.get("features_used") or {},
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


@router.post("/academic/upload")
async def upload_academic_results(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload WASSCE / academic results (PDF or image).

    Stores the file server-side, extracts grades from PDFs with pypdf
    (text + WASSCE parsing), and unlocks Get Recommendations.
    """
    data = await file.read()
    filename = file.filename or "academic_results.pdf"
    error = validate_academic_file(filename, file.content_type, len(data))
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    stored_name, _path = save_academic_file(str(current_user.id), filename, data)
    grades = await extract_grades_with_ai(
        filename=filename,
        content_type=file.content_type,
        data=data,
    )

    # Replace academic records when we extracted grades
    if grades:
        await db.execute(
            delete(AcademicRecord).where(AcademicRecord.user_id == current_user.id)
        )
        for row in grades:
            db.add(
                AcademicRecord(
                    user_id=current_user.id,
                    subject=row["subject"],
                    grade=row["grade"],
                    exam_type="WASSCE",
                )
            )

    current_user.learner_profile = merge_academic_upload_into_profile(
        current_user.learner_profile if isinstance(current_user.learner_profile, dict) else {},
        filename=filename,
        stored_name=stored_name,
        grades=grades,
    )
    await db.commit()
    await db.refresh(current_user)

    return {
        "success": True,
        "filename": filename,
        "grades_extracted": bool(grades),
        "records": grades,
        "message": (
            f"Uploaded {filename}. Extracted {len(grades)} subject grade(s)."
            if grades
            else (
                "WASSCE results could not be extracted from this file. "
                "Please re-upload a clearer PDF or image (full results page, good lighting), "
                "or use a text-based PDF export."
            )
        ),
        "code": None if grades else "wassce_extraction_failed",
        "title": None if grades else "WASSCE results could not be extracted",
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
