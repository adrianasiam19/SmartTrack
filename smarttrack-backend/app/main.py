"""
main.py — Atlas API entry point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai_chat.router import router as ai_chat_router
from app.assessment.daily_streak import router as daily_streak_router
from app.assessment.router import router as assessment_router
from app.auth.router import router as auth_router
from app.config import settings
from app.database import engine
from app.revision.router import router as revision_router
from app.assessment.starter_router import router as starter_router
from app.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    # Nothing to do on startup for now (Alembic handles migrations separately)
    yield
    # Cleanly close all DB connections on shutdown
    await engine.dispose()


app = FastAPI(
    title="Atlas API",
    description="AI-powered career guidance platform for SHS students",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow your Next.js frontend to call the API cross-origin
# Allow localhost on all dev ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
        "http://127.0.0.1:3005",
        "http://192.168.127.1:3000",
        "http://192.168.127.1:3001",
        "http://192.168.127.1:3002",
        "http://192.168.127.1:3003",
        "http://192.168.127.1:3004",
        "http://192.168.127.1:3005",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(assessment_router, prefix="/api/v1")
app.include_router(ai_chat_router, prefix="/api/v1")
app.include_router(daily_streak_router, prefix="/api/v1")
app.include_router(revision_router, prefix="/api/v1")
app.include_router(starter_router, prefix="/api/v1")


# ── Root route ────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "Atlas API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "Not available"
    }


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "atlas-api"}
