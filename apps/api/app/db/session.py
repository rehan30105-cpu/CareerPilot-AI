"""Async database session and engine configuration."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_debug,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Yield an async database session for dependency injection."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create all tables defined on the SQLAlchemy Base.

    In production, Alembic migrations manage schema. This helper is used
    only for local development convenience when no migration history exists.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
