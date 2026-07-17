from pydantic import BaseModel
from typing import Dict, Optional, List

class QuestionResponse(BaseModel):
    id: int
    domain: str
    question: str
    options: Dict[str, str]
    answer_hash: Optional[str] = None

    class Config:
        from_attributes = True

class AssessmentListResponse(BaseModel):
    questions: List[QuestionResponse]
    total: int

class CalibrationStartRequest(BaseModel):
    category: str
    domain: Optional[str] = None

class CalibrationStartResponse(BaseModel):
    questions: List[QuestionResponse]
    initial_theta: float

class NextQuestionResponse(BaseModel):
    questions: List[QuestionResponse]


class SubmitResponseRequest(BaseModel):
    question_id: int
    selected_option: str
    time_taken_ms: int
    retries: int = 0

class TelemetrySubmitRequest(BaseModel):
    question_id: int
    selected_option: str
    time_taken_seconds: float
    hints_used: int = 0
    is_correct: Optional[bool] = None  # Frontend-computed; used for AI-generated questions

class TelemetrySubmitResponse(BaseModel):
    status: str
    is_correct: bool
    next_questions: List[QuestionResponse]

class ExplanationRequest(BaseModel):
    question_id: int
    selected_option: str

class ExplanationResponse(BaseModel):
    explanation: str

class DashboardResponse(BaseModel):
    radar_chart: Dict[str, float]
    behavioral_traits: Dict[str, float]
    overall_score: float
    career_matches: List[Dict]

class LeaderboardEntry(BaseModel):
    rank: int
    user_name: str
    score: float
    school: str
    is_me: bool = False

class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]

class SaveAcademicRecordsRequest(BaseModel):
    exam_type: str # WASSCE, UTME, etc.
    results: Dict[str, str] # {"Math": "A1", ...}

class LearningModuleResponse(BaseModel):
    id: int
    title: str
    description: str
    content_url: str

class RecommendedModulesResponse(BaseModel):
    modules: List[LearningModuleResponse]


# ── AI Challenge Generation ──────────────────────────────────────────────────

class GenerateChallengeRequest(BaseModel):
    """Request to generate a challenge using AI (DeepSeek / NVIDIA)."""
    category: str  # Logic, Quantitative Thinking, Scientific Thinking, etc.
    difficulty: str  # Beginner, Intermediate, Advanced
    programme: str  # General Science, General Arts
    concept: Optional[str] = None  # Optional specific concept to focus on

    class Config:
        examples = [
            {
                "category": "Logic",
                "difficulty": "Intermediate",
                "programme": "General Science",
                "concept": "Deductive reasoning",
            }
        ]


class ChallengeOption(BaseModel):
    """A single option for a challenge question."""
    text: str


class PsychometricCardOption(BaseModel):
    """A single option in a psychometric card."""
    value: str
    label: str


class PsychometricCardResponse(BaseModel):
    """A psychometric insight card for the frontend (no trait weights)."""
    id: str
    category: str
    question: str
    display: str
    options: List[PsychometricCardOption]


class PsychometricSubmitRequest(BaseModel):
    """A user's answer to a psychometric insight card."""
    question_id: str
    answer: str


class PsychometricSubmitResponse(BaseModel):
    """Response after saving a psychometric answer."""
    success: bool
    message: str


class GeneratedChallenge(BaseModel):
    """A generated challenge question from AI."""
    category: str
    difficulty: str
    concept: str
    question: str
    options: List[str]  # Exactly 4 options
    correct_answer: str  # Must be one of the options
    explanation: str


class GenerateChallengeResponse(BaseModel):
    """Response from challenge generation endpoint."""
    success: bool
    data: Optional[GeneratedChallenge] = None
    error: Optional[str] = None
