"""Business profile repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business_profile import BusinessProfile
from app.repositories.base import BaseRepository


class BusinessProfileRepository(BaseRepository[BusinessProfile]):
    def __init__(self, db: AsyncSession):
        super().__init__(BusinessProfile, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> BusinessProfile | None:
        """Get the business profile for a specific user."""
        result = await self.db.execute(
            select(BusinessProfile).where(BusinessProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, user_id: uuid.UUID, data: dict) -> BusinessProfile:
        """Create or update the business profile for a user."""
        existing = await self.get_by_user_id(user_id)
        if existing:
            update_data = {k: v for k, v in data.items() if v is not None}
            for key, value in update_data.items():
                setattr(existing, key, value)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            data["user_id"] = user_id
            return await self.create(data)
