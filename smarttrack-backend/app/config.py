from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


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

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
