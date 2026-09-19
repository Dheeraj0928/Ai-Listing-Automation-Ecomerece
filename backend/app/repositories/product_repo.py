"""Product repository."""

import uuid

from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_id_with_relations(self, product_id: uuid.UUID) -> Product | None:
        """Get product with images and DNA eagerly loaded."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.images), selectinload(Product.dna))
            .where(Product.id == product_id, Product.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str, user_id: uuid.UUID) -> Product | None:
        """Find product by SKU for a specific user."""
        result = await self.db.execute(
            select(Product).where(
                Product.sku == sku,
                Product.user_id == user_id,
                Product.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def sku_exists(self, sku: str, exclude_id: uuid.UUID | None = None) -> bool:
        """Check if a SKU already exists, optionally excluding a specific product."""
        query = select(Product).where(Product.sku == sku, Product.deleted_at.is_(None))
        if exclude_id:
            query = query.where(Product.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        status: str | None = None,
        category_id: uuid.UUID | None = None,
    ) -> tuple[list[Product], int]:
        """List products for a user with search, filtering, and pagination."""
        filters = [Product.user_id == user_id, Product.deleted_at.is_(None)]

        if status:
            filters.append(Product.status == status)
        if category_id:
            filters.append(Product.category_id == category_id)
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    Product.product_name.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.brand.ilike(search_term),
                )
            )

        # Count
        count_query = select(func.count()).select_from(Product)
        for f in filters:
            count_query = count_query.where(f)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()

        # Fetch
        query = (
            select(Product)
            .options(selectinload(Product.images))
            .where(*filters)
            .order_by(Product.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)
        products = list(result.scalars().all())

        return products, total

    async def count_by_status(self, user_id: uuid.UUID, status: str) -> int:
        """Count products by status for a user."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Product)
            .where(
                Product.user_id == user_id,
                Product.status == status,
                Product.deleted_at.is_(None),
            )
        )
        return result.scalar_one()

    async def count_low_stock(self, user_id: uuid.UUID, threshold: int = 10) -> int:
        """Count products with stock below threshold."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Product)
            .where(
                Product.user_id == user_id,
                Product.stock <= threshold,
                Product.deleted_at.is_(None),
            )
        )
        return result.scalar_one()
