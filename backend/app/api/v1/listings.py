"""Marketplace listings API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.listing import (
    ListingGenerateRequest,
    ListingListResponse,
    ListingResponse,
    ListingUpdateRequest,
    ListingValidateResponse,
)
from app.services.listing_service import ListingService
from app.services.listing_generator_service import ListingGeneratorService
from app.services.listing_validator_service import ListingValidatorService

router = APIRouter(prefix="/listings", tags=["Listings"])


def _get_listing_service(db: AsyncSession = Depends(get_db)) -> ListingService:
    return ListingService(db)


def _get_generator_service(db: AsyncSession = Depends(get_db)) -> ListingGeneratorService:
    return ListingGeneratorService(db)


def _get_validator_service(db: AsyncSession = Depends(get_db)) -> ListingValidatorService:
    return ListingValidatorService(db)


@router.get("", response_model=ListingListResponse, summary="List all listings")
async def list_listings(
    marketplace: str | None = Query(default=None),
    status: str | None = Query(default=None),
    product_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    svc: ListingService = Depends(_get_listing_service),
):
    return await svc.list_listings(
        user_id=user.id,
        page=page,
        page_size=page_size,
        marketplace=marketplace,
        status=status,
        product_id=product_id,
    )


@router.post("/generate", summary="Generate AI listings for a product")
async def generate_listings(
    body: ListingGenerateRequest,
    user: User = Depends(get_current_user),
    gen_svc: ListingGeneratorService = Depends(_get_generator_service),
):
    listings = await gen_svc.generate_listings(
        user_id=user.id,
        product_id=body.product_id,
        marketplaces=body.marketplaces,
        tone=body.tone,
        provider_name=body.provider,
    )
    return {"status": "success", "data": [l.model_dump() for l in listings]}


@router.get("/{listing_id}", response_model=ListingResponse, summary="Get listing detail")
async def get_listing(
    listing_id: uuid.UUID,
    user: User = Depends(get_current_user),
    svc: ListingService = Depends(_get_listing_service),
):
    return await svc.get_listing(user_id=user.id, listing_id=listing_id)


@router.put("/{listing_id}", response_model=ListingResponse, summary="Update listing data")
async def update_listing(
    listing_id: uuid.UUID,
    body: ListingUpdateRequest,
    user: User = Depends(get_current_user),
    svc: ListingService = Depends(_get_listing_service),
):
    return await svc.update_listing(user_id=user.id, listing_id=listing_id, data=body)


@router.post("/{listing_id}/validate", response_model=ListingValidateResponse, summary="Validate listing")
async def validate_listing(
    listing_id: uuid.UUID,
    user: User = Depends(get_current_user),
    val_svc: ListingValidatorService = Depends(_get_validator_service),
):
    return await val_svc.validate_listing(user_id=user.id, listing_id=listing_id)


@router.post("/{listing_id}/approve", response_model=ListingResponse, summary="Approve listing")
async def approve_listing(
    listing_id: uuid.UUID,
    user: User = Depends(get_current_user),
    svc: ListingService = Depends(_get_listing_service),
):
    return await svc.approve_listing(user_id=user.id, listing_id=listing_id)


@router.post("/{listing_id}/publish", summary="Publish listing to marketplace")
async def publish_listing(
    listing_id: uuid.UUID,
    user: User = Depends(get_current_user),
    svc: ListingService = Depends(_get_listing_service),
):
    result = await svc.publish_listing(user_id=user.id, listing_id=listing_id)
    return {"status": "success", "data": result}


@router.get("/{listing_id}/versions", summary="Get listing version history")
async def get_listing_versions(
    listing_id: uuid.UUID,
    user: User = Depends(get_current_user),
    svc: ListingService = Depends(_get_listing_service),
):
    versions = await svc.get_versions(user_id=user.id, listing_id=listing_id)
    return {"status": "success", "data": [v.model_dump() for v in versions]}


@router.delete("/{listing_id}", summary="Delete listing")
async def delete_listing(
    listing_id: uuid.UUID,
    user: User = Depends(get_current_user),
    svc: ListingService = Depends(_get_listing_service),
):
    await svc.delete_listing(user_id=user.id, listing_id=listing_id)
    return {"status": "success", "message": "Listing deleted"}


@router.post("/bulk-validate", summary="Bulk validate listings")
async def bulk_validate(
    listing_ids: list[uuid.UUID],
    user: User = Depends(get_current_user),
    val_svc: ListingValidatorService = Depends(_get_validator_service),
):
    results = await val_svc.bulk_validate(user_id=user.id, listing_ids=listing_ids)
    return {"status": "success", "data": results}
