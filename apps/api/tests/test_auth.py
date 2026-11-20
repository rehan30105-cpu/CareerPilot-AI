"""Authentication endpoint tests.

Uses the isolated SQLite test database provided by conftest.py.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_register_success(client):
    """Successful registration returns the created user without password hash."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "SecurePass123",
        "full_name": "New User",
    })
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "hashed_password" not in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Registering the same email twice returns 409."""
    await client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "password": "SecurePass123",
    })
    response = await client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "password": "DifferentPass456",
    })
    assert response.status_code == 409, response.text


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """Registration with an invalid email is rejected."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "not-an-email",
        "password": "SecurePass123",
    })
    assert response.status_code in (400, 422), response.text


@pytest.mark.asyncio
async def test_register_short_password(client):
    """Registration with a short password is rejected."""
    response = await client.post("/api/v1/auth/register", json={
        "email": "shortpw@example.com",
        "password": "short",
    })
    assert response.status_code in (400, 422), response.text


@pytest.mark.asyncio
async def test_login_success(client):
    """Successful login returns access and refresh tokens."""
    await client.post("/api/v1/auth/register", json={
        "email": "loginuser@example.com",
        "password": "SecurePass123",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "loginuser@example.com",
        "password": "SecurePass123",
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Login with wrong password returns 401 without revealing account existence."""
    await client.post("/api/v1/auth/register", json={
        "email": "wrongpw@example.com",
        "password": "SecurePass123",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "wrongpw@example.com",
        "password": "WrongPassword!",
    })
    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Login with nonexistent email returns the same 401 as wrong password."""
    response = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "SecurePass123",
    })
    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client):
    """Accessing /auth/me without a token returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(client):
    """Accessing /auth/me with a valid access token returns the user profile."""
    await client.post("/api/v1/auth/register", json={
        "email": "meuser@example.com",
        "password": "SecurePass123",
        "full_name": "Me User",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "meuser@example.com",
        "password": "SecurePass123",
    })
    token = login_resp.json()["access_token"]

    response = await client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "meuser@example.com"
    assert data["full_name"] == "Me User"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_refresh_token(client):
    """Using a valid refresh token returns a new access token."""
    await client.post("/api/v1/auth/register", json={
        "email": "refreshuser@example.com",
        "password": "SecurePass123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "refreshuser@example.com",
        "password": "SecurePass123",
    })
    refresh_token = login_resp.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    """Using an invalid refresh token returns 401."""
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": "invalid-token",
    })
    assert response.status_code == 401, response.text


@pytest.mark.asyncio
async def test_logout(client):
    """Logout clears the session and returns success."""
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Logged out successfully"
