"""
main.py — SmartTrack API entry point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.config import settings
from app.database import engine
from app.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    # Nothing to do on startup for now (Alembic handles migrations separately)
    yield
    # Cleanly close all DB connections on shutdown
    await engine.dispose()


app = FastAPI(
    title="SmartTrack API",
    description="AI-powered career guidance platform for SHS students",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow your Next.js frontend to call the API cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "smarttrack-api"}
