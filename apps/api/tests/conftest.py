"""Pytest configuration and shared fixtures for CareerPilot AI backend tests.

Provides an isolated SQLite test database (aiosqlite) for each test function,
overriding the FastAPI app's database dependency. Production code continues
to use PostgreSQL + asyncpg via DATABASE_URL.
"""

import asyncio
import os
import tempfile
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.v1.deps import get_db_session as _get_db_session
from app.db.base import Base
from app.main import app

# ---------------------------------------------------------------------------
# Test database engine (SQLite, ephemeral)
# ---------------------------------------------------------------------------

_TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "careerpilot_test.db")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{_TEST_DB_PATH}"

# Remove any leftover test database from a previous interrupted run
if os.path.exists(_TEST_DB_PATH):
    os.remove(_TEST_DB_PATH)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a test database session for dependency injection."""
    async with TestAsyncSessionLocal() as session:
        yield session


async def init_test_db() -> None:
    """Create all tables in the test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_test_db() -> None:
    """Drop all tables from the test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# FastAPI dependency override
# ---------------------------------------------------------------------------

# Override the get_db_session dependency to use the test database
app.dependency_overrides[_get_db_session] = get_test_db


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _setup_test_database():
    """Create the test database schema once per test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(init_test_db())
        yield
    finally:
        loop.run_until_complete(drop_test_db())
        loop.run_until_complete(test_engine.dispose())
        loop.close()
        if os.path.exists(_TEST_DB_PATH):
            os.remove(_TEST_DB_PATH)


@pytest.fixture
async def clean_db() -> AsyncGenerator[None, None]:
    """Ensure a clean database state for each test function.

    Rolls back all changes after the test by deleting all rows from every
    table, providing full isolation between tests.
    """
    yield
    # Clean up all data after each test
    async with TestAsyncSessionLocal() as session:
        async with session.begin():
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(table.delete())


@pytest.fixture
async def client(clean_db) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing the FastAPI app with test database."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

