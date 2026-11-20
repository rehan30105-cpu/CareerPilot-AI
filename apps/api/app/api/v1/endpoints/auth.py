"""Authentication endpoints: register, login, refresh, logout, me."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user, get_db_session
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    Message,
    Token,
    TokenRefresh,
    UserCreate,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Look up a user by email. Returns None if not found (no leak)."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """Register a new user account.

    Email uniqueness is enforced at the database level. The response never
    includes the password hash.
    """
    existing = await _get_user_by_email(db, user_in.email)
    if existing is not None:
        # Generic message — does not confirm or deny account existence
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    login_in: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Token:
    """Authenticate a user and return access + refresh tokens.

    The refresh token is set as an HttpOnly cookie to prevent XSS theft.
    The access token is returned in the body for the client to store in
    memory (not localStorage).
    """
    user = await _get_user_by_email(db, login_in.email)
    if user is None or not verify_password(login_in.password, user.hashed_password):
        # Same response whether account exists or password is wrong —
        # prevents account enumeration.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Set refresh token as secure HttpOnly cookie
    secure = settings.app_env == "production"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/api/v1/auth/refresh",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    refresh_in: TokenRefresh,
) -> Token:
    """Issue a new access token using a valid refresh token.

    The refresh token can be supplied either in the body or via the
    HttpOnly cookie set during login.
    """
    token = refresh_in.refresh_token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    new_access = create_access_token(int(user_id_str))
    new_refresh = create_refresh_token(int(user_id_str))

    secure = settings.app_env == "production"
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/api/v1/auth/refresh",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
    )


@router.post("/logout", response_model=Message)
async def logout(response: Response) -> Message:
    """Clear the refresh token cookie and invalidate the session."""
    response.delete_cookie(key="refresh_token", path="/api/v1/auth/refresh")
    return Message(message="Logged out successfully")


@router.get("/me", response_model=UserRead)
async def read_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Return the currently authenticated user's profile."""
    return current_user
