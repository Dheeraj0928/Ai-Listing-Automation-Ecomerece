"""Authentication service."""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
)


class AuthService:
    """Handles authentication business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def signup(self, data: SignupRequest) -> tuple[User, TokenResponse]:
        """Register a new user and return tokens."""
        if await self.user_repo.email_exists(data.email):
            raise ConflictError(f"An account with email '{data.email}' already exists")

        user = await self.user_repo.create(
            {
                "email": data.email,
                "password_hash": hash_password(data.password),
                "full_name": data.full_name,
                "phone": data.phone,
                "is_active": True,
                "is_verified": False,
            }
        )

        tokens = self._generate_tokens(user)
        return user, tokens

    async def login(self, data: LoginRequest) -> tuple[User, TokenResponse]:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(data.email)

        if user is None or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Your account has been deactivated")

        await self.user_repo.update_last_login(user)
        tokens = self._generate_tokens(user)
        return user, tokens

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Validate refresh token and issue new access token."""
        payload = decode_token(refresh_token)

        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid or expired refresh token")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)

        if user is None or not user.is_active:
            raise UnauthorizedError("User not found or deactivated")

        return self._generate_tokens(user)

    async def forgot_password(self, email: str) -> str | None:
        """Generate password reset token. Returns token for dev (console log)."""
        user = await self.user_repo.get_by_email(email)
        if user is None:
            # Don't reveal whether email exists
            return None

        reset_token = create_reset_token(str(user.id))
        # In production, send this via email service
        # For Phase 1, we log it to console
        print(f"[DEV] Password reset token for {email}: {reset_token}")
        return reset_token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using a valid reset token."""
        payload = decode_token(token)

        if payload is None or payload.get("type") != "reset":
            raise UnauthorizedError("Invalid or expired reset token")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)

        if user is None:
            raise UnauthorizedError("Invalid reset token")

        user.password_hash = hash_password(new_password)
        await self.db.flush()
        return True

    def _generate_tokens(self, user: User) -> TokenResponse:
        """Generate access and refresh token pair."""
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"email": user.email, "name": user.full_name},
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
