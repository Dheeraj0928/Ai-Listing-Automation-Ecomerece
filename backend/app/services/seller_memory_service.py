"""Seller memory service — learn once, reuse forever."""

import math
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.seller_memory_repo import SellerMemoryRepository
from app.schemas.seller_memory import (
    SellerMemoryCreate,
    SellerMemoryListResponse,
    SellerMemoryResolveResponse,
    SellerMemoryResponse,
    SellerMemoryUpdate,
)


class SellerMemoryService:
    """Seller memory business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.memory_repo = SellerMemoryRepository(db)

    async def create_memory(
        self, user_id: uuid.UUID, data: SellerMemoryCreate
    ) -> SellerMemoryResponse:
        """Save a new memory entry."""
        memory_data = data.model_dump(exclude_none=True)
        memory_data["user_id"] = user_id

        memory = await self.memory_repo.create(memory_data)
        return SellerMemoryResponse.model_validate(memory)

    async def list_memories(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 50,
        field_name: str | None = None,
        scope: str | None = None,
        marketplace: str | None = None,
    ) -> SellerMemoryListResponse:
        """List memory entries with filters."""
        offset = (page - 1) * page_size
        items, total = await self.memory_repo.list_for_user(
            user_id=user_id,
            offset=offset,
            limit=page_size,
            field_name=field_name,
            scope=scope,
            marketplace=marketplace,
        )

        return SellerMemoryListResponse(
            items=[SellerMemoryResponse.model_validate(m) for m in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update_memory(
        self, user_id: uuid.UUID, memory_id: uuid.UUID, data: SellerMemoryUpdate
    ) -> SellerMemoryResponse:
        """Update a memory entry."""
        memory = await self.memory_repo.get_by_id(memory_id)
        if memory is None or memory.user_id != user_id:
            raise NotFoundError("Memory entry", str(memory_id))

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(memory, key, value)

        await self.db.flush()
        await self.db.refresh(memory)
        return SellerMemoryResponse.model_validate(memory)

    async def delete_memory(self, user_id: uuid.UUID, memory_id: uuid.UUID) -> bool:
        """Deactivate a memory entry (soft-delete)."""
        memory = await self.memory_repo.get_by_id(memory_id)
        if memory is None or memory.user_id != user_id:
            raise NotFoundError("Memory entry", str(memory_id))

        memory.is_active = False
        await self.db.flush()
        return True

    async def resolve_field(
        self,
        user_id: uuid.UUID,
        field_name: str,
        marketplace: str | None = None,
        product_id: uuid.UUID | None = None,
    ) -> SellerMemoryResolveResponse:
        """Resolve a field value using hierarchy: product > marketplace > global."""
        entry = await self.memory_repo.resolve_field(
            user_id=user_id,
            field_name=field_name,
            marketplace=marketplace,
            product_id=product_id,
        )

        if entry:
            # Increment usage count
            entry.usage_count += 1
            entry.last_used_at = datetime.now(timezone.utc)
            await self.db.flush()

            return SellerMemoryResolveResponse(
                field_name=field_name,
                resolved_value=entry.field_value,
                source_scope=entry.scope,
                source_marketplace=entry.marketplace,
                source_id=entry.id,
            )

        return SellerMemoryResolveResponse(
            field_name=field_name,
            resolved_value=None,
        )
