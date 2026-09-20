"""Marketplace account repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.marketplace_account import MarketplaceAccount
from app.repositories.base import BaseRepository


class MarketplaceRepository(BaseRepository[MarketplaceAccount]):
    def __init__(self, db: AsyncSession):
        super().__init__(MarketplaceAccount, db)

    async def get_user_accounts(self, user_id: uuid.UUID) -> list[MarketplaceAccount]:
        """Get all marketplace accounts for a user."""
        result = await self.db.execute(
            select(MarketplaceAccount)
            .where(MarketplaceAccount.user_id == user_id)
            .order_by(MarketplaceAccount.marketplace)
        )
        return list(result.scalars().all())

    async def get_by_marketplace(
        self, user_id: uuid.UUID, marketplace: str
    ) -> MarketplaceAccount | None:
        """Get a specific marketplace account for a user."""
        result = await self.db.execute(
            select(MarketplaceAccount).where(
                MarketplaceAccount.user_id == user_id,
                MarketplaceAccount.marketplace == marketplace,
            )
        )
        return result.scalar_one_or_none()

    async def marketplace_exists(self, user_id: uuid.UUID, marketplace: str) -> bool:
        """Check if a marketplace account already exists for the user."""
        account = await self.get_by_marketplace(user_id, marketplace)
        return account is not None
