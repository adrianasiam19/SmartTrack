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

    @property
    def google_client_id_clean(self) -> str:
        """Client ID without accidental http(s):// paste prefix."""
        value = (self.GOOGLE_CLIENT_ID or "").strip()
        if value.startswith("https://"):
            value = value[len("https://") :]
        if value.startswith("http://"):
            value = value[len("http://") :]
        return value.strip()

    def google_oauth_configured(self) -> bool:
        client_id = self.google_client_id_clean
        secret = (self.GOOGLE_CLIENT_SECRET or "").strip()
        return bool(
            client_id
            and secret
            and "your-google-client-id" not in client_id
            and secret != "your-google-client-secret"
            and client_id.endswith(".apps.googleusercontent.com")
        )

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

    # ── Email / password reset (Resend) ─────────────────────────────────────
    # Required in production (startup fails if missing). Optional in development
    # — non-production still returns `dev_reset_link` for local testing.
    RESEND_API_KEY: str = ""
    MAIL_FROM: str = ""

    # Legacy SMTP keys (unused — kept so old .env files still parse)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True

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

    # ── ML programme recommendations (Decision Tree is primary) ───────────
    ML_RECOMMENDATIONS_ENABLED: bool = True
    ML_RECOMMENDATIONS_TOP_N: int = 8
    # Legacy aliases (still accepted via env for older .env files)
    ML_ALTERNATE_ENABLED: bool = True
    ML_ALTERNATE_TOP_N: int = 5
    # When true (or ENVIRONMENT=development), attach recommendation debug payload.
    RECOMMENDATION_DEBUG: bool = False

    PIXABAY_API_KEY: str = ""
    EDUCATIONAL_IMAGES_ENABLED: bool = True
    EDUCATIONAL_IMAGE_CACHE_PATH: str = "data/educational_image_cache.json"
    # YouTube Data API v3 (optional). Without it, Atlas uses a public search fallback.
    YOUTUBE_API_KEY: str = ""
    EDUCATIONAL_VIDEOS_ENABLED: bool = True
    EDUCATIONAL_VIDEO_CACHE_PATH: str = "data/educational_video_cache.json"
    EDUCATIONAL_VIDEO_CACHE_TTL_SECONDS: float = 86_400
    EDUCATIONAL_VIDEO_LIMIT: int = 3
    # Bump when challenge question payload / UI contract changes (invalidates old clients).
    CHALLENGE_FORMAT_VERSION: int = 12
    # Parallel LLM question generation concurrency for a single level start.
    CHALLENGE_GEN_CONCURRENCY: int = 6
    # How long a prefetched question set stays valid (seconds).
    CHALLENGE_PREFETCH_TTL_SECONDS: int = 900
    # Rolling buffer: how many upcoming levels to keep prepared per learner.
    CHALLENGE_PREFETCH_BUFFER_LEVELS: int = 3
    # Max seconds start_level waits for an in-flight prefetch before regenerating.
    CHALLENGE_PREFETCH_WAIT_SECONDS: float = 75.0
    # When Dashboard/Challenges call /prefetch/warm, wait this long for the
    # *current* playable level to become ready (fire-and-forget from FE).
    CHALLENGE_PREFETCH_WARM_WAIT_SECONDS: float = 55.0
    # Prefer academic bank before calling the LLM (keep False — LLM is primary).
    CHALLENGE_BANK_FIRST: bool = False
    # LLM attempts per question before bank/fallback (image/format misses retry first).
    CHALLENGE_LLM_ATTEMPTS: int = 3
    # DeepSeek read timeout per question call (seconds).
    CHALLENGE_LLM_TIMEOUT_SECONDS: float = 20.0
    # Fail DNS/connect quickly so offline DeepSeek cannot hang Start Level.
    CHALLENGE_LLM_CONNECT_TIMEOUT_SECONDS: float = 3.0
    # Legacy: force no challenge images (same as CHALLENGE_IMAGES_MODE=off).
    CHALLENGE_FAST_SKIP_IMAGES: bool = False
    # Challenge visuals (Option B default):
    #   local_only — attach Atlas SVG / existing cache only (no live search; fast & safe)
    #   off        — text-only challenges
    #   full       — allow live Wikimedia/Openverse/Pixabay (slower; not for demo path)
    CHALLENGE_IMAGES_MODE: str = "local_only"

    # ── Notifications / future push (Stage 9) ─────────────────────────────
    # Generation always persists in-app. Push channels stay dormant until
    # PUSH_NOTIFICATIONS_ENABLED=true AND credentials are configured.
    PUSH_NOTIFICATIONS_ENABLED: bool = False
    # Firebase Admin credentials (JSON string OR path). Unused until FCM is wired.
    FCM_CREDENTIALS_JSON: str = ""
    FCM_CREDENTIALS_PATH: str = ""
    # Web Push VAPID key pair (unused until Web Push is wired).
    WEB_PUSH_VAPID_PUBLIC_KEY: str = ""
    WEB_PUSH_VAPID_PRIVATE_KEY: str = ""
    WEB_PUSH_VAPID_SUBJECT: str = "mailto:support@atlas.local"

    # ── Personal Progress / future leaderboard module (Stage 5) ───────────
    # Keep false for MVP (personal growth only). Flip to true + implement
    # progress.future_modules.build_leaderboard_module_payload to mount rankings.
    PROGRESS_LEADERBOARD_MODULE_ENABLED: bool = False

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
