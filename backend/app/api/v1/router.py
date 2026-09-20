"""V1 API router — aggregates all v1 route modules."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.products import router as products_router
from app.api.v1.business_profiles import router as business_profiles_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.ai import router as ai_router
from app.api.v1.listings import router as listings_router
from app.api.v1.marketplace_accounts import router as marketplace_accounts_router
from app.api.v1.seller_memory import router as seller_memory_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router)
v1_router.include_router(products_router)
v1_router.include_router(business_profiles_router)
v1_router.include_router(dashboard_router)
v1_router.include_router(notifications_router)
v1_router.include_router(ai_router)
v1_router.include_router(listings_router)
v1_router.include_router(marketplace_accounts_router)
v1_router.include_router(seller_memory_router)
