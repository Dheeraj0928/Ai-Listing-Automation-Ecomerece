"""FastAPI dependencies for authentication and common operations."""

import uuid

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repo import UserRepository


async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT from Authorization header, return the authenticated user."""
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError("Invalid authorization header format. Use: Bearer <token>")

    token = authorization[7:]
    payload = decode_token(token)

    if payload is None:
        raise UnauthorizedError("Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Invalid token payload")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Invalid token payload")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise UnauthorizedError("User not found")

    if not user.is_active:
        raise UnauthorizedError("Account is deactivated")

    return user
