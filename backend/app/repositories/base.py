"""Generic base repository with CRUD operations."""

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing generic CRUD operations for any SQLAlchemy model."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        """Get a single record by its UUID primary key."""
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        filters: list | None = None,
        order_by: Any = None,
    ) -> list[ModelType]:
        """Get paginated records with optional filters and ordering."""
        query = select(self.model)
        if filters:
            for f in filters:
                query = query.where(f)
        if order_by is not None:
            query = query.order_by(order_by)
        else:
            query = query.order_by(self.model.created_at.desc())
        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, filters: list | None = None) -> int:
        """Count records matching optional filters."""
        query = select(func.count()).select_from(self.model)
        if filters:
            for f in filters:
                query = query.where(f)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def create(self, data: dict) -> ModelType:
        """Create a new record from a dictionary of attributes."""
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def update_by_id(self, id: uuid.UUID, data: dict) -> ModelType | None:
        """Update a record by ID with the given data dictionary."""
        # Remove None values to avoid overwriting with NULL
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return await self.get_by_id(id)

        await self.db.execute(
            update(self.model).where(self.model.id == id).values(**update_data)
        )
        await self.db.flush()
        return await self.get_by_id(id)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        """Hard delete a record by ID."""
        instance = await self.get_by_id(id)
        if instance is None:
            return False
        await self.db.delete(instance)
        await self.db.flush()
        return True

    async def soft_delete(self, id: uuid.UUID) -> ModelType | None:
        """Soft delete by setting deleted_at timestamp."""
        from datetime import datetime, timezone
        return await self.update_by_id(id, {"deleted_at": datetime.now(timezone.utc)})
