"""Seller memory API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.seller_memory import (
    SellerMemoryCreate,
    SellerMemoryListResponse,
    SellerMemoryResolveResponse,
    SellerMemoryResponse,
    SellerMemoryUpdate,
)
from app.services.seller_memory_service import SellerMemoryService

router = APIRouter(prefix="/memory", tags=["Seller Memory"])


def _get_service(db: AsyncSession = Depends(get_db)) -> SellerMemoryService:
    return SellerMemoryService(db)


@router.get("", response_model=SellerMemoryListResponse, summary="List all memorized values")
async def list_memories(
    field_name: str | None = Query(default=None),
    scope: str | None = Query(default=None),
    marketplace: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    user: User = Depends(get_current_user),
    svc: SellerMemoryService = Depends(_get_service),
):
    return await svc.list_memories(
        user_id=user.id,
        page=page,
        page_size=page_size,
        field_name=field_name,
        scope=scope,
        marketplace=marketplace,
    )


@router.post("", response_model=SellerMemoryResponse, summary="Save a new memory entry")
async def create_memory(
    body: SellerMemoryCreate,
    user: User = Depends(get_current_user),
    svc: SellerMemoryService = Depends(_get_service),
):
    return await svc.create_memory(user_id=user.id, data=body)


@router.put("/{memory_id}", response_model=SellerMemoryResponse, summary="Update memory entry")
async def update_memory(
    memory_id: uuid.UUID,
    body: SellerMemoryUpdate,
    user: User = Depends(get_current_user),
    svc: SellerMemoryService = Depends(_get_service),
):
    return await svc.update_memory(user_id=user.id, memory_id=memory_id, data=body)


@router.delete("/{memory_id}", summary="Deactivate memory entry")
async def delete_memory(
    memory_id: uuid.UUID,
    user: User = Depends(get_current_user),
    svc: SellerMemoryService = Depends(_get_service),
):
    await svc.delete_memory(user_id=user.id, memory_id=memory_id)
    return {"status": "success", "message": "Memory entry deactivated"}


@router.get("/resolve/{field_name}", response_model=SellerMemoryResolveResponse, summary="Resolve field by hierarchy")
async def resolve_field(
    field_name: str,
    marketplace: str | None = Query(default=None),
    product_id: uuid.UUID | None = Query(default=None),
    user: User = Depends(get_current_user),
    svc: SellerMemoryService = Depends(_get_service),
):
    return await svc.resolve_field(
        user_id=user.id,
        field_name=field_name,
        marketplace=marketplace,
        product_id=product_id,
    )
