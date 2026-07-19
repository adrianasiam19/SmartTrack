import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)

MAX_DB_RETRIES = 3
DB_RETRY_DELAY_S = 2

# ── Async engine — connects to Neon PostgreSQL ────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",  # SQL logging in dev only
    pool_pre_ping=True,    # Verify connections before use (good for Neon's serverless)
    pool_recycle=300,       # Recycle connections every 5 mins (Neon best practice)
    pool_size=5,            # Keep a small pool ready
    max_overflow=10,        # Allow burst connections
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields a database session per request.
    Retries on transient connection failures (Neon serverless idle/reset).
    Business-logic errors from route handlers propagate immediately.
    """
    last_exc: Exception | None = None
    for attempt in range(1, MAX_DB_RETRIES + 1):
        try:
            async with AsyncSessionLocal() as session:
                # Verify the connection is alive with a lightweight query
                await session.execute(text("SELECT 1"))
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
                finally:
                    await session.close()
            return  # success
        except (OperationalError, DBAPIError) as exc:
            # Only retry on connection-level / DBAPI errors
            last_exc = exc
            logger.warning(
                "DB connection attempt %d/%d failed: %s",
                attempt, MAX_DB_RETRIES, exc,
            )
            if attempt < MAX_DB_RETRIES:
                await asyncio.sleep(DB_RETRY_DELAY_S * attempt)
        except Exception:
            # Business logic errors — propagate immediately
            raise
    # All connection attempts exhausted
    logger.error("All %d database connection attempts failed.", MAX_DB_RETRIES)
    raise last_exc  # type:ignore[misc]
