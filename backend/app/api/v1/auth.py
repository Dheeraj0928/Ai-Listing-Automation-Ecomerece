"""Authentication API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
)
from app.schemas.common import SuccessResponse
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=dict, status_code=201)
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    """Register a new seller account."""
    service = AuthService(db)
    user, tokens = await service.signup(data)
    return {
        "user": UserResponse.model_validate(user).model_dump(),
        "tokens": tokens.model_dump(),
    }


@router.post("/login", response_model=dict)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    service = AuthService(db)
    user, tokens = await service.login(data)
    return {
        "user": UserResponse.model_validate(user).model_dump(),
        "tokens": tokens.model_dump(),
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    service = AuthService(db)
    return await service.refresh_token(data.refresh_token)


@router.post("/forgot-password", response_model=SuccessResponse)
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Request a password reset email."""
    service = AuthService(db)
    await service.forgot_password(data.email)
    # Always return success to not reveal whether email exists
    return SuccessResponse(message="If an account exists with this email, a reset link has been sent.")


@router.post("/reset-password", response_model=SuccessResponse)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password using a valid reset token."""
    service = AuthService(db)
    await service.reset_password(data.token, data.new_password)
    return SuccessResponse(message="Password has been reset successfully.")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    data: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)
