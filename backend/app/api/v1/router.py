"""V1 API router — aggregates all v1 route modules."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.products import router as products_router
from app.api.v1.business_profiles import router as business_profiles_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.notifications import router as notifications_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router)
v1_router.include_router(products_router)
v1_router.include_router(business_profiles_router)
v1_router.include_router(dashboard_router)
v1_router.include_router(notifications_router)
