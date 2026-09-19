"""User schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """User profile response."""
    id: UUID
    email: EmailStr
    full_name: str
    phone: str | None = None
    avatar_url: str | None = None
    is_active: bool
    is_verified: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    """Request body for updating user profile."""
    full_name: str | None = Field(None, min_length=2, max_length=255)
    phone: str | None = Field(None, max_length=20)
    avatar_url: str | None = Field(None, max_length=500)
