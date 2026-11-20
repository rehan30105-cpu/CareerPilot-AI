"""Tests for health endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """GET /health should return ok status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "CareerPilot AI"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_db_health_endpoint(client):
    """GET /health/db should return a response (may be degraded without Postgres)."""
    response = await client.get("/api/v1/health/db")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["database"] == "postgresql"
