"""Product API routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.product import (
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    status: str | None = Query(None, pattern="^(draft|active|archived)$"),
    category_id: uuid.UUID | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List products with search, filtering, and pagination."""
    service = ProductService(db)
    return await service.list_products(
        user=user,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        category_id=category_id,
    )


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product."""
    service = ProductService(db)
    return await service.create_product(user, data)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single product by ID."""
    service = ProductService(db)
    return await service.get_product(user, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing product."""
    service = ProductService(db)
    return await service.update_product(user, product_id, data)


@router.delete("/{product_id}", response_model=SuccessResponse)
async def delete_product(
    product_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a product."""
    service = ProductService(db)
    await service.delete_product(user, product_id)
    return SuccessResponse(message="Product deleted successfully")
