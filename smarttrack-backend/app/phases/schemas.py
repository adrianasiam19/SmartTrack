from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class LevelPublic(BaseModel):
    id: int
    number: int
    difficulty_baseline: int
    status: str
    score: Optional[float] = None
    attempts: int = 0
    completed_at: Optional[datetime] = None


class PhasePublic(BaseModel):
    id: int
    number: int
    name: str
    description: Optional[str] = None
    status: str
    levels: List[LevelPublic] = Field(default_factory=list)


class ProgressionMeResponse(BaseModel):
    phases: List[PhasePublic]
    current_phase_number: int
    current_level_number: int


class StartLevelResponse(BaseModel):
    session_id: int
    level_id: int
    phase_number: int
    level_number: int
    is_replay: bool
    questions: List[dict[str, Any]]
    subject_mix: Optional[dict[str, int]] = None
    format_version: Optional[int] = None
    question_count: Optional[int] = None
    from_prefetch: bool = False


class PrefetchStatusResponse(BaseModel):
    status: str
    level_id: Optional[int] = None
    format_version: Optional[int] = None
    question_count: int = 0
    error: Optional[str] = None
    cached_level_id: Optional[int] = None
    ready_levels: List[int] = Field(default_factory=list)
    fetching_levels: List[int] = Field(default_factory=list)
    error_levels: List[int] = Field(default_factory=list)
    buffer_size: Optional[int] = None
    buffer: List[dict[str, Any]] = Field(default_factory=list)


class WarmPrefetchResponse(BaseModel):
    status: str = "idle"
    warmed: List[int] = Field(default_factory=list)
    ready_count: int = 0
    fetching_count: int = 0
    question_count: int = 0
    ready_levels: List[int] = Field(default_factory=list)
    fetching_levels: List[int] = Field(default_factory=list)
    buffer: List[dict[str, Any]] = Field(default_factory=list)
    primary_ready: bool = False

class SubmitAnswerRequest(BaseModel):
    question_id: int
    answer: str
    time_taken_seconds: Optional[float] = None


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    explanation: Optional[str] = None
    correct_count: int
    wrong_count: int
    xp_earned: int = 0
    user_xp: Optional[int] = None
    rank: Optional[str] = None
    learning_nudge: Optional[dict[str, Any]] = None


class CompleteSessionResponse(BaseModel):
    passed: bool
    score: float
    threshold: float
    level_completed: bool
    next: Optional[str] = None  # psychometric_checkpoint | None
    phase_number: Optional[int] = None
    level_id: Optional[int] = None
    next_level_id: Optional[int] = None
    next_level_number: Optional[int] = None
    session_xp: int = 0
    user_xp: Optional[int] = None
    rank: Optional[str] = None
    learning_nudge: Optional[dict[str, Any]] = None
