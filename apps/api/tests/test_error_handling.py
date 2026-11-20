"""Tests for centralized error handling."""

import pytest


@pytest.mark.asyncio
async def test_unknown_route_returns_404(client):
    """A non-existent route should return 404, not a 500."""
    response = await client.get("/nonexistent")
    assert response.status_code == 404
