"""Business profile API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.business_profile import (
    AutoFillConfigRequest,
    BusinessProfileRequest,
    BusinessProfileResponse,
)
from app.services.business_profile_service import BusinessProfileService

router = APIRouter(prefix="/business-profile", tags=["Business Profile"])


@router.get("", response_model=BusinessProfileResponse | None)
async def get_business_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the seller's business profile."""
    service = BusinessProfileService(db)
    return await service.get_profile(user)


@router.put("", response_model=BusinessProfileResponse)
async def upsert_business_profile(
    data: BusinessProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or update the business profile."""
    service = BusinessProfileService(db)
    return await service.upsert_profile(user, data)


@router.patch("/auto-fill", response_model=BusinessProfileResponse)
async def update_auto_fill_config(
    data: AutoFillConfigRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update auto-fill configuration for business fields."""
    service = BusinessProfileService(db)
    return await service.update_auto_fill_config(user, data)
