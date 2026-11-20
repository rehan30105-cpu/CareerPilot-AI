"""Authentication request/response schemas."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Registration request."""

    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password must be between 8 and 128 characters.",
    )
    full_name: str | None = Field(
        default=None, max_length=255, description="Optional full name."
    )


class UserRead(BaseModel):
    """User response — never includes password hash."""

    id: int
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Refresh token request."""

    refresh_token: str


class Message(BaseModel):
    """Generic message response."""

    message: str
