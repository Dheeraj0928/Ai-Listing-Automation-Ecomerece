"""Marketplace account schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MarketplaceAccountCreate(BaseModel):
    """Connect a new marketplace account."""
    marketplace: str = Field(..., pattern="^(amazon|flipkart|meesho)$")
    account_id: str | None = None
    account_name: str | None = None
    credentials: dict | None = Field(None, description="API keys/tokens (will be encrypted)")
    config: dict | None = None


class MarketplaceAccountUpdate(BaseModel):
    """Update marketplace account config."""
    account_name: str | None = None
    credentials: dict | None = None
    config: dict | None = None


class MarketplaceAccountResponse(BaseModel):
    """Marketplace account response."""
    id: UUID
    user_id: UUID
    marketplace: str
    account_id: str | None = None
    account_name: str | None = None
    status: str
    config: dict | None = None
    last_sync_at: datetime | None = None
    last_error: str | None = None
    listing_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MarketplaceAccountListResponse(BaseModel):
    """List of marketplace accounts."""
    items: list[MarketplaceAccountResponse]
    total: int
