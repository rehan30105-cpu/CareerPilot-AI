"""Authentication dependencies for FastAPI route protection."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.models.user import User

# Bearer token scheme for Authorization header
bearer_scheme = HTTPBearer(auto_error=False)


async def get_db_session() -> AsyncSession:
    """Yield a database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Retrieve the currently authenticated user from a JWT.

    Returns None when no credentials are provided (callers decide whether
    to require authentication or allow anonymous access).
    Raises HTTPException 401 when credentials are malformed or invalid.
    """
    if credentials is None:
        return None

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(User, int(user_id_str))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return user


async def get_current_active_user(
    current_user: Annotated[object, Depends(get_current_user)],
):
    """Require an authenticated, active user. Raises 401 if not authenticated."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


# Re-export get_db for backward compatibility
get_db = get_db_session
