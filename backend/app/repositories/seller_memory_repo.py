"""Seller memory repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seller_memory import SellerMemory
from app.repositories.base import BaseRepository


class SellerMemoryRepository(BaseRepository[SellerMemory]):
    def __init__(self, db: AsyncSession):
        super().__init__(SellerMemory, db)

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
        field_name: str | None = None,
        scope: str | None = None,
        marketplace: str | None = None,
    ) -> tuple[list[SellerMemory], int]:
        """List memory entries for a user with optional filters."""
        filters = [SellerMemory.user_id == user_id, SellerMemory.is_active.is_(True)]
        if field_name:
            filters.append(SellerMemory.field_name.ilike(f"%{field_name}%"))
        if scope:
            filters.append(SellerMemory.scope == scope)
        if marketplace:
            filters.append(SellerMemory.marketplace == marketplace)

        items = await self.get_all(offset=offset, limit=limit, filters=filters)
        total = await self.count(filters=filters)
        return items, total

    async def resolve_field(
        self,
        user_id: uuid.UUID,
        field_name: str,
        marketplace: str | None = None,
        product_id: uuid.UUID | None = None,
    ) -> SellerMemory | None:
        """Resolve a field value using hierarchy: product > marketplace > global."""
        # Try product-level first
        if product_id:
            result = await self.db.execute(
                select(SellerMemory).where(
                    SellerMemory.user_id == user_id,
                    SellerMemory.field_name == field_name,
                    SellerMemory.scope == "product",
                    SellerMemory.product_id == product_id,
                    SellerMemory.is_active.is_(True),
                ).order_by(SellerMemory.priority.desc()).limit(1)
            )
            entry = result.scalar_one_or_none()
            if entry:
                return entry

        # Try marketplace-level
        if marketplace:
            result = await self.db.execute(
                select(SellerMemory).where(
                    SellerMemory.user_id == user_id,
                    SellerMemory.field_name == field_name,
                    SellerMemory.scope == "marketplace",
                    SellerMemory.marketplace == marketplace,
                    SellerMemory.is_active.is_(True),
                ).order_by(SellerMemory.priority.desc()).limit(1)
            )
            entry = result.scalar_one_or_none()
            if entry:
                return entry

        # Fall back to global
        result = await self.db.execute(
            select(SellerMemory).where(
                SellerMemory.user_id == user_id,
                SellerMemory.field_name == field_name,
                SellerMemory.scope == "global",
                SellerMemory.is_active.is_(True),
            ).order_by(SellerMemory.priority.desc()).limit(1)
        )
        return result.scalar_one_or_none()
