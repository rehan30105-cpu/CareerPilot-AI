"""Health check endpoints.

Distinguishes API health (always available) from database health
(requires PostgreSQL connectivity).
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.db.session import engine

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str
    detail: str | None = None


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    """API health — always returns ok if the FastAPI process is running."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version="0.1.0",
        environment=settings.app_env,
    )


@router.get("/health/db", response_model=DatabaseHealthResponse, tags=["health"])
async def database_health() -> DatabaseHealthResponse:
    """Database health — verifies PostgreSQL connectivity."""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return DatabaseHealthResponse(
            status="ok",
            database="postgresql",
            detail="connected",
        )
    except Exception as exc:  # noqa: BLE001
        return DatabaseHealthResponse(
            status="degraded",
            database="postgresql",
            detail=str(exc),
        )
