import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # ── Arena structure (Phase 2) ──────────────────────────────────────────
    arena: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    """
    Which arena the question belongs to:
      "logic" | "quantitative" | "scientific" | "communication"
    """
    difficulty_tier: Mapped[str | None] = mapped_column(String(20), nullable=True)
    """
    "Bronze" | "Silver" | "Gold" — roughly maps to SHS 1 / SHS 2 / SHS 3.
    """
    shs_levels: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    """
    JSON list of SHS levels this question is appropriate for, e.g. ["SHS 1", "SHS 2"].
    """
    template_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    """
    The template family this question was generated from (e.g. "logic-seq-add-001").
    Used for anti-cheating — ensures students don't get the same template repeatedly.
    """

    question: Mapped[str] = mapped_column(String(1000), nullable=False)
    options: Mapped[dict] = mapped_column(JSON, nullable=False)  # {"A": "...", "B": "...", etc}
    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)  # A, B, C, or D
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # IRT Parameters
    difficulty_a: Mapped[float] = mapped_column(nullable=False, default=1.0) # discrimination
    difficulty_b: Mapped[float] = mapped_column(nullable=False, default=0.0) # difficulty
    difficulty_c: Mapped[float] = mapped_column(nullable=False, default=0.25) # guessing (e.g. 25% for 4 options)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Question id={self.id} arena={self.arena} tier={self.difficulty_tier}>"


class UserSkillEstimate(Base):
    """Tracks a user's skill estimate (theta) per domain using IRT."""
    __tablename__ = "user_skill_estimates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Skill parameters
    theta: Mapped[float] = mapped_column(nullable=False, default=0.0)
    standard_error: Mapped[float] = mapped_column(nullable=False, default=1.0)

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<UserSkillEstimate user_id={self.user_id} domain={self.domain} theta={self.theta}>"


class Response(Base):
    """Tracks individual answers for Behavioral Intelligence."""
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Telemetry
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_taken_seconds: Mapped[float] = mapped_column(nullable=False)
    hints_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Response user_id={self.user_id} question_id={self.question_id} correct={self.correct}>"


class BehavioralProfile(Base):
    """Tracks derived behavioral traits for a user."""
    __tablename__ = "behavioral_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trait: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[float] = mapped_column(nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(nullable=False, default=0.0)

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<BehavioralProfile user_id={self.user_id} trait={self.trait} value={self.value}>"


class Leaderboard(Base):
    """Precomputed leaderboard scores for fast retrieval."""
    __tablename__ = "leaderboards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # "Overall", "Math", "Logic", etc.
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # "Science", "Arts", etc., or "Global"
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(nullable=False, default=0.0)
    rank: Mapped[int] = mapped_column(Integer, nullable=True)

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Leaderboard user_id={self.user_id} domain={self.domain} score={self.score}>"


class LearningModule(Base):
    """Micro-content (2-3 min) to teach a concept before testing."""
    __tablename__ = "learning_modules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    domain: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown
    difficulty_level: Mapped[float] = mapped_column(nullable=False, default=0.0) # Matches IRT theta

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<LearningModule id={self.id} domain={self.domain} title='{self.title}'>"


class CurriculumLesson(Base):
    """Official SHS 1/2 curriculum source used by the grounded AI tutor."""
    __tablename__ = "curriculum_lessons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    curriculum_id: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    programme: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    shs_levels: Mapped[list] = mapped_column(JSON, nullable=False)
    unit_id: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    source_content: Mapped[dict] = mapped_column(JSON, nullable=False)
    search_text: Mapped[str] = mapped_column(Text, nullable=False)
    ai_content_by_level: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    ai_content_version: Mapped[str] = mapped_column(
        String(30), nullable=False, default="v1"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<CurriculumLesson curriculum_id={self.curriculum_id} "
            f"subject={self.subject}>"
        )


class PsychometricCard(Base):
    """
    Psychometric Insight Cards injected every 3-5 challenge questions.
    These feel natural and engaging — students shouldn't feel they are
    taking a psychological assessment. Responses feed into the
    behavioural trait analysis and programme recommendations.
    """
    __tablename__ = "psychometric_cards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    card_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    options: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Optional trait mapping: e.g. {"A": "analytical", "B": "creative", ...}
    trait_mapping: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<PsychometricCard id={self.id} card_id={self.card_id}>"


class PsychometricResponse(Base):
    """Stores a user's answer to a psychometric insight card."""
    __tablename__ = "psychometric_responses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    card_id: Mapped[str] = mapped_column(String(50), nullable=False)
    answer: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<PsychometricResponse user_id={self.user_id} card_id={self.card_id}>"


class StarterArenaResponse(Base):
    """Durable record of every psychometric and cognitive Starter Arena answer."""
    __tablename__ = "starter_arena_responses"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "session_id",
            "question_id",
            name="uq_starter_response_user_session_question",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(String(120), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cognitive_skill: Mapped[str | None] = mapped_column(String(100), nullable=True)
    question_format: Mapped[str] = mapped_column(String(40), nullable=False)
    options: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    time_taken_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class DailyStreakProgress(Base):
    """
    Tracks each user's progress per daily streak subject and level.
    """
    __tablename__ = "daily_streak_progress"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject_id: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    """
    One of: "core-mathematics", "integrated-science", "english-language", "social-studies"
    """
    level_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0–100
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship("User", backref="daily_streak_progress")

    def __repr__(self) -> str:
        return f"<DailyStreakProgress user_id={self.user_id} subject={self.subject_id} level={self.level_id}>"


class ChallengeSession(Base):
    """
    Mixed-subject challenge session for a Phase Level (legacy hub fields retained).
    """
    __tablename__ = "challenge_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Legacy hub level 1–3; prefer level_id for Phase/Level progression
    challenge_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    level_id: Mapped[int | None] = mapped_column(
        ForeignKey("levels.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_replay: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress")
    total_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_subject_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship("User", backref="challenge_sessions")

    def __repr__(self) -> str:
        return f"<ChallengeSession id={self.id} user_id={self.user_id} level={self.challenge_level}>"


class ChallengeResponse(Base):
    """
    Individual answer within a challenge session (ChallengeQuestion shape).
    """
    __tablename__ = "challenge_responses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("challenge_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject: Mapped[str] = mapped_column(String(50), nullable=False)
    question_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False, default="mcq")
    options: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Text: ordering/matching JSON answers can exceed 500 chars
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    user_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    # Effective difficulty after per-subject adaptive adjustment
    difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_taken_seconds: Mapped[float | None] = mapped_column(nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    session: Mapped["ChallengeSession"] = relationship("ChallengeSession", backref="responses")

    def __repr__(self) -> str:
        return f"<ChallengeResponse id={self.id} session_id={self.session_id} subject={self.subject}>"


