"""Seller memory schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SellerMemoryCreate(BaseModel):
    """Create a new seller memory entry."""
    field_name: str = Field(..., min_length=1, max_length=255)
    field_value: str = Field(..., min_length=1)
    source: str = Field("manual", pattern="^(manual|ai_suggested|imported)$")
    scope: str = Field("global", pattern="^(global|marketplace|product)$")
    marketplace: str | None = Field(None, pattern="^(amazon|flipkart|meesho)$")
    product_id: UUID | None = None
    priority: int = Field(0, ge=0, le=100)


class SellerMemoryUpdate(BaseModel):
    """Update a seller memory entry."""
    field_value: str | None = Field(None, min_length=1)
    source: str | None = Field(None, pattern="^(manual|ai_suggested|imported)$")
    scope: str | None = Field(None, pattern="^(global|marketplace|product)$")
    marketplace: str | None = None
    priority: int | None = Field(None, ge=0, le=100)
    is_active: bool | None = None


class SellerMemoryResponse(BaseModel):
    """Seller memory entry response."""
    id: UUID
    user_id: UUID
    field_name: str
    field_value: str
    source: str
    scope: str
    marketplace: str | None = None
    product_id: UUID | None = None
    priority: int
    is_active: bool
    usage_count: int
    last_used_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SellerMemoryListResponse(BaseModel):
    """Paginated seller memory list."""
    items: list[SellerMemoryResponse]
    total: int
    page: int
    page_size: int


class SellerMemoryResolveResponse(BaseModel):
    """Resolved value for a field using hierarchy."""
    field_name: str
    resolved_value: str | None = None
    source_scope: str | None = None
    source_marketplace: str | None = None
    source_id: UUID | None = None
