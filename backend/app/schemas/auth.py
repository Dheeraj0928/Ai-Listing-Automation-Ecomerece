"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Request body for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str | None = Field(None, max_length=20)


class LoginRequest(BaseModel):
    """Request body for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Request body for refreshing access token."""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Request body for forgot password."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request body for password reset."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    """Request body for changing password while logged in."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
