from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ────────────────────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT ─────────────────────────────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Google OAuth ─────────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # ── DeepSeek AI ────────────────────────────────────────────────────────────
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # ── NVIDIA AI ────────────────────────────────────────────────────────────
    NVIDIA_API_KEY: str = ""
    NVIDIA_MODEL: str = "meta/llama-3.1-8b-instruct"

    # ── App ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"

    # ── Email / password reset (optional — logs reset link in development) ─
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    MAIL_FROM: str = ""

    # ── Phase / Level progression ───────────────────────────────────────────
    # Pass threshold kept for analytics/config compatibility; progression no longer gates on it.
    LEVEL_PASS_THRESHOLD: float = 0.70
    CHALLENGE_QUESTIONS_PER_SESSION: int = 10  # legacy; live count from level_question_count()
    SUBJECT_MIX: str = "english:3,core_maths:3,integrated_science:2,social_studies:2"
    DIFFICULTY_ROLLING_WINDOW: int = 20
    DIFFICULTY_LOW_ACCURACY: float = 0.50
    # Mostly-correct subjects step up difficulty for the next level.
    DIFFICULTY_HIGH_ACCURACY: float = 0.60
    DIFFICULTY_ADJ_STEP: int = 1
    DIFFICULTY_MIN: int = 1
    DIFFICULTY_MAX: int = 15
    LEARNING_NUDGE_LEVELS: int = 2
    # How many recent answered texts to exclude to reduce cross-level repeats.
    CHALLENGE_EXCLUDE_HISTORY: int = 80
    PSYCHO_CHECKPOINT_COUNT: int = 8  # one question from each of 8 varied categories

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def subject_mix_map(self) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for part in self.SUBJECT_MIX.split(","):
            part = part.strip()
            if not part or ":" not in part:
                continue
            subject, count = part.split(":", 1)
            result[subject.strip()] = int(count.strip())
        return result


settings = Settings()
