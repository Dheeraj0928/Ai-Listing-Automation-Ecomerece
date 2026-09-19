"""Dashboard and notification schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Main dashboard statistics."""
    total_products: int
    active_listings: int
    draft_listings: int
    needs_review_listings: int
    publishing_errors: int
    low_stock_products: int


class MarketplaceBreakdown(BaseModel):
    """Per-marketplace statistics."""
    marketplace: str
    products: int
    listings: int
    errors: int
    published: int


class RecentActivity(BaseModel):
    """Single activity feed item."""
    id: UUID
    action: str
    entity_type: str
    entity_id: UUID | None = None
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardResponse(BaseModel):
    """Full dashboard response."""
    stats: DashboardStats
    marketplace_breakdown: list[MarketplaceBreakdown]
    recent_activity: list[RecentActivity]


class NotificationResponse(BaseModel):
    """Notification response."""
    id: UUID
    type: str
    category: str
    title: str
    message: str
    data: dict | None = None
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Paginated notification list."""
    items: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
