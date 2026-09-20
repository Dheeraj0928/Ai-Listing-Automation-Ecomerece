"""Product image API routes."""

import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.image_service import ImageService

router = APIRouter(prefix="/products/{product_id}/images", tags=["Product Images"])


@router.get("")
async def list_images(
    product_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all images for a product."""
    service = ImageService(db)
    return await service.get_images(user.id, product_id)


@router.post("", status_code=201)
async def upload_images(
    product_id: uuid.UUID,
    files: list[UploadFile] = File(...),
    image_type: str = Query("main", pattern="^(main|white_bg|lifestyle|closeup|feature|size_spec)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload one or more images to a product."""
    service = ImageService(db)
    return await service.upload_images(user.id, product_id, files, image_type)


@router.delete("/{image_id}", response_model=SuccessResponse)
async def delete_image(
    product_id: uuid.UUID,
    image_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a product image."""
    service = ImageService(db)
    await service.delete_image(user.id, product_id, image_id)
    return SuccessResponse(message="Image deleted successfully")


@router.put("/reorder")
async def reorder_images(
    product_id: uuid.UUID,
    image_ids: list[uuid.UUID],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reorder product images by providing a sorted list of image IDs."""
    service = ImageService(db)
    return await service.reorder_images(user.id, product_id, image_ids)


@router.put("/{image_id}/primary")
async def set_primary_image(
    product_id: uuid.UUID,
    image_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set a specific image as the primary product image."""
    service = ImageService(db)
    return await service.set_primary(user.id, product_id, image_id)
