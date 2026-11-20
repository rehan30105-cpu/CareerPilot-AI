"""Security utilities: argon2id password hashing and JWT token management."""

import datetime as dt
from typing import Any

from jose import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

# Argon2id hasher with OWASP-recommended parameters
_password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Hash a plaintext password using argon2id.

    Never returns or stores plaintext passwords.
    """
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an argon2id hash.

    Returns False on mismatch rather than raising, so callers can
    uniformly treat invalid credentials as authentication failure
    without leaking whether the account exists.
    """
    try:
        _password_hasher.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False


def create_access_token(subject: str | int, expires_delta: int | None = None) -> str:
    """Create a JWT access token.

    Args:
        subject: User ID (stringified) to encode as the token subject.
        expires_delta: Optional override for expiration in minutes.
    """
    now = dt.datetime.now(dt.timezone.utc)
    expire = now + dt.timedelta(
        minutes=expires_delta or settings.access_token_expire_minutes
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_refresh_token(subject: str | int) -> str:
    """Create a JWT refresh token with longer expiration."""
    now = dt.datetime.now(dt.timezone.utc)
    expire = now + dt.timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT.

    Raises jwt.PyJWTError on invalid/expired tokens.
    """
    return jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
