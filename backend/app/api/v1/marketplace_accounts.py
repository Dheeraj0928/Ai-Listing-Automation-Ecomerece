"""Marketplace accounts API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.marketplace import (
    MarketplaceAccountCreate,
    MarketplaceAccountListResponse,
    MarketplaceAccountResponse,
    MarketplaceAccountUpdate,
)
from app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/marketplaces", tags=["Marketplaces"])


def _get_service(db: AsyncSession = Depends(get_db)) -> MarketplaceService:
    return MarketplaceService(db)


@router.get("", response_model=MarketplaceAccountListResponse, summary="List connected marketplaces")
async def list_accounts(
    user: User = Depends(get_current_user),
    svc: MarketplaceService = Depends(_get_service),
):
    return await svc.list_accounts(user_id=user.id)


@router.post("", response_model=MarketplaceAccountResponse, summary="Connect a new marketplace")
async def connect_marketplace(
    body: MarketplaceAccountCreate,
    user: User = Depends(get_current_user),
    svc: MarketplaceService = Depends(_get_service),
):
    return await svc.connect_marketplace(user_id=user.id, data=body)


@router.get("/{marketplace}", response_model=MarketplaceAccountResponse, summary="Get marketplace account")
async def get_account(
    marketplace: str,
    user: User = Depends(get_current_user),
    svc: MarketplaceService = Depends(_get_service),
):
    return await svc.get_account(user_id=user.id, marketplace=marketplace)


@router.put("/{marketplace}", response_model=MarketplaceAccountResponse, summary="Update marketplace config")
async def update_account(
    marketplace: str,
    body: MarketplaceAccountUpdate,
    user: User = Depends(get_current_user),
    svc: MarketplaceService = Depends(_get_service),
):
    return await svc.update_account(user_id=user.id, marketplace=marketplace, data=body)


@router.delete("/{marketplace}", summary="Disconnect marketplace")
async def disconnect_marketplace(
    marketplace: str,
    user: User = Depends(get_current_user),
    svc: MarketplaceService = Depends(_get_service),
):
    await svc.disconnect_marketplace(user_id=user.id, marketplace=marketplace)
    return {"status": "success", "message": f"{marketplace.title()} disconnected"}


@router.post("/{marketplace}/sync", summary="Trigger manual sync")
async def sync_marketplace(
    marketplace: str,
    user: User = Depends(get_current_user),
    svc: MarketplaceService = Depends(_get_service),
):
    result = await svc.sync_marketplace(user_id=user.id, marketplace=marketplace)
    return {"status": "success", "data": result}
