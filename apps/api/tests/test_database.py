"""Test database configuration using SQLite (aiosqlite) for isolated testing.

This module provides an async SQLite engine and session factory used *only*
during pytest runs. Production code continues to use PostgreSQL + asyncpg
via DATABASE_URL. The test database is ephemeral (file-based, deleted after
the test session) and provides full isolation between tests.
"""

import os
import tempfile
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base

# Use a file-based SQLite database for tests. :memory: creates a new database
# per connection, which breaks async session sharing. A temp file gives us a
# single shared database that we can create/drop tables on per test.
_TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "careerpilot_test.db")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{_TEST_DB_PATH}"

# Remove any leftover test database from a previous run
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
    """Yield a test database session."""
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


async def cleanup_test_db_file() -> None:
    """Delete the test database file after the session."""
    await test_engine.dispose()
    if os.path.exists(_TEST_DB_PATH):
        os.remove(_TEST_DB_PATH)
