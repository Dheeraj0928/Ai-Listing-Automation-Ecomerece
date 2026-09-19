"""Listing repository."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.marketplace_listing import MarketplaceListing
from app.repositories.base import BaseRepository


class ListingRepository(BaseRepository[MarketplaceListing]):
    def __init__(self, db: AsyncSession):
        super().__init__(MarketplaceListing, db)

    async def count_by_marketplace_status(
        self, user_id: uuid.UUID, marketplace: str | None = None, status: str | None = None
    ) -> int:
        """Count listings by marketplace and/or status."""
        filters = [MarketplaceListing.user_id == user_id, MarketplaceListing.deleted_at.is_(None)]
        if marketplace:
            filters.append(MarketplaceListing.marketplace == marketplace)
        if status:
            filters.append(MarketplaceListing.status == status)

        result = await self.db.execute(
            select(func.count()).select_from(MarketplaceListing).where(*filters)
        )
        return result.scalar_one()

    async def get_marketplace_breakdown(self, user_id: uuid.UUID) -> list[dict]:
        """Get listing counts grouped by marketplace for dashboard."""
        result = await self.db.execute(
            select(
                MarketplaceListing.marketplace,
                func.count().label("total"),
                func.count().filter(MarketplaceListing.status == "published").label("published"),
                func.count().filter(MarketplaceListing.status == "error").label("errors"),
            )
            .where(MarketplaceListing.user_id == user_id, MarketplaceListing.deleted_at.is_(None))
            .group_by(MarketplaceListing.marketplace)
        )
        return [
            {
                "marketplace": row.marketplace,
                "listings": row.total,
                "published": row.published,
                "errors": row.errors,
            }
            for row in result.all()
        ]
