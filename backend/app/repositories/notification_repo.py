"""Notification repository."""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)

    async def get_for_user(
        self, user_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[Notification], int]:
        """Get paginated notifications for a user."""
        filters = [Notification.user_id == user_id]

        count_result = await self.db.execute(
            select(func.count()).select_from(Notification).where(*filters)
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Notification)
            .where(*filters)
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        notifications = list(result.scalars().all())

        return notifications, total

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        """Get count of unread notifications for a user."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
        )
        return result.scalar_one()

    async def mark_as_read(self, notification_id: uuid.UUID) -> None:
        """Mark a single notification as read."""
        await self.db.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        await self.db.flush()

    async def mark_all_as_read(self, user_id: uuid.UUID) -> None:
        """Mark all notifications as read for a user."""
        await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        await self.db.flush()

    async def create_notification(
        self,
        user_id: uuid.UUID,
        type: str,
        category: str,
        title: str,
        message: str,
        data: dict | None = None,
    ) -> Notification:
        """Create a new notification."""
        return await self.create(
            {
                "user_id": user_id,
                "type": type,
                "category": category,
                "title": title,
                "message": message,
                "data": data,
            }
        )
