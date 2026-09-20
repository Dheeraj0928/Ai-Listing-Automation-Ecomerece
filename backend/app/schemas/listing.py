"""Listing schemas for marketplace listings."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ListingGenerateRequest(BaseModel):
    """Request to generate listings for a product."""
    product_id: UUID
    marketplaces: list[str] = Field(..., min_length=1, description="e.g. ['amazon', 'flipkart', 'meesho']")
    tone: str = Field("professional", pattern="^(professional|casual|luxury|technical)$")
    provider: str | None = Field(None, description="AI provider override")


class ListingUpdateRequest(BaseModel):
    """Update listing data manually."""
    listing_data: dict | None = None
    marketplace_specific_data: dict | None = None
    status: str | None = Field(None, pattern="^(draft|ai_generated|validated|needs_review|approved|publishing|published|error)$")


class ListingVersionResponse(BaseModel):
    """A single listing version snapshot."""
    id: UUID
    listing_id: UUID
    version_number: int
    snapshot: dict | None = None
    changes: dict | None = None
    changed_by: str | None = None
    change_reason: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ListingResponse(BaseModel):
    """Full listing response."""
    id: UUID
    product_id: UUID
    user_id: UUID
    marketplace: str
    marketplace_listing_id: str | None = None
    status: str
    listing_data: dict | None = None
    marketplace_specific_data: dict | None = None
    completion_percentage: Decimal | None = None
    validation_results: dict | None = None
    version: int
    error_message: str | None = None
    published_at: datetime | None = None
    last_synced_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ListingListResponse(BaseModel):
    """Paginated listing list."""
    items: list[ListingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ListingValidateResponse(BaseModel):
    """Validation result for a listing."""
    is_valid: bool
    completion_percentage: float
    errors: list[dict] = []
    warnings: list[dict] = []


class ListingPublishResponse(BaseModel):
    """Result of a publish operation."""
    success: bool
    listing_id: UUID
    marketplace: str
    marketplace_listing_id: str | None = None
    message: str
