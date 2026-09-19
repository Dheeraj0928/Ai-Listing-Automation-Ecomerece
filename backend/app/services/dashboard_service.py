"""Dashboard service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.listing_repo import ListingRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardStats,
    MarketplaceBreakdown,
    RecentActivity,
)


class DashboardService:
    """Dashboard statistics and activity feed."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.listing_repo = ListingRepository(db)
        self.audit_repo = AuditRepository(db)

    async def get_dashboard(self, user: User) -> DashboardResponse:
        """Get full dashboard data."""
        stats = await self._get_stats(user)
        marketplace_breakdown = await self._get_marketplace_breakdown(user)
        recent_activity = await self._get_recent_activity(user)

        return DashboardResponse(
            stats=stats,
            marketplace_breakdown=marketplace_breakdown,
            recent_activity=recent_activity,
        )

    async def _get_stats(self, user: User) -> DashboardStats:
        """Calculate dashboard statistics."""
        total_products = await self.product_repo.count(
            filters=[
                self.product_repo.model.user_id == user.id,
                self.product_repo.model.deleted_at.is_(None),
            ]
        )

        active_listings = await self.listing_repo.count_by_marketplace_status(
            user_id=user.id, status="published"
        )
        draft_listings = await self.listing_repo.count_by_marketplace_status(
            user_id=user.id, status="draft"
        )
        needs_review = await self.listing_repo.count_by_marketplace_status(
            user_id=user.id, status="needs_review"
        )
        errors = await self.listing_repo.count_by_marketplace_status(
            user_id=user.id, status="error"
        )
        low_stock = await self.product_repo.count_low_stock(user.id)

        return DashboardStats(
            total_products=total_products,
            active_listings=active_listings,
            draft_listings=draft_listings,
            needs_review_listings=needs_review,
            publishing_errors=errors,
            low_stock_products=low_stock,
        )

    async def _get_marketplace_breakdown(self, user: User) -> list[MarketplaceBreakdown]:
        """Get per-marketplace listing breakdown."""
        breakdown_data = await self.listing_repo.get_marketplace_breakdown(user.id)

        # Always return all 3 marketplaces
        marketplace_map = {item["marketplace"]: item for item in breakdown_data}
        result = []

        for mp in ["amazon", "flipkart", "meesho"]:
            data = marketplace_map.get(mp, {"listings": 0, "published": 0, "errors": 0})
            result.append(
                MarketplaceBreakdown(
                    marketplace=mp,
                    products=0,  # Will be accurate when products are linked to marketplaces
                    listings=data.get("listings", 0),
                    errors=data.get("errors", 0),
                    published=data.get("published", 0),
                )
            )

        return result

    async def _get_recent_activity(self, user: User) -> list[RecentActivity]:
        """Get recent activity feed from audit logs."""
        logs = await self.audit_repo.get_recent_activity(user.id, limit=15)

        action_messages = {
            "product_created": "New product created",
            "product_updated": "Product updated",
            "product_deleted": "Product deleted",
            "business_profile_updated": "Business profile updated",
            "auto_fill_config_updated": "Auto-fill settings updated",
            "listing_created": "Listing created",
            "listing_published": "Listing published",
            "listing_validated": "Listing validated",
            "user_login": "Logged in",
        }

        return [
            RecentActivity(
                id=log.id,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                message=self._build_activity_message(log, action_messages),
                created_at=log.created_at,
            )
            for log in logs
        ]

    def _build_activity_message(self, log, action_messages: dict) -> str:
        """Build a human-readable activity message from an audit log entry."""
        base_message = action_messages.get(log.action, log.action.replace("_", " ").title())

        if log.new_value:
            name = log.new_value.get("name") or log.new_value.get("sku") or ""
            if name:
                return f"{base_message}: {name}"

        return base_message
