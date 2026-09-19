"""Notification API routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.notification_repo import NotificationRepository
from app.schemas.common import SuccessResponse
from app.schemas.dashboard import NotificationListResponse, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated notifications for the current user."""
    repo = NotificationRepository(db)
    offset = (page - 1) * page_size
    notifications, total = await repo.get_for_user(user.id, offset, page_size)
    unread_count = await repo.get_unread_count(user.id)

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size,
    )


@router.put("/{notification_id}/read", response_model=SuccessResponse)
async def mark_as_read(
    notification_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    repo = NotificationRepository(db)
    await repo.mark_as_read(notification_id)
    return SuccessResponse(message="Notification marked as read")


@router.put("/read-all", response_model=SuccessResponse)
async def mark_all_as_read(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    repo = NotificationRepository(db)
    await repo.mark_all_as_read(user.id)
    return SuccessResponse(message="All notifications marked as read")


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get count of unread notifications."""
    repo = NotificationRepository(db)
    count = await repo.get_unread_count(user.id)
    return {"unread_count": count}
