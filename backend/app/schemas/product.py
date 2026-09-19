"""Product schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    """Request body for creating a product."""
    sku: str = Field(..., min_length=1, max_length=100)
    product_name: str = Field(..., min_length=1, max_length=500)
    brand: str | None = Field(None, max_length=255)
    category_id: UUID | None = None
    subcategory: str | None = Field(None, max_length=255)
    product_type: str | None = Field(None, max_length=255)
    description: str | None = None
    short_description: str | None = None
    bullet_points: list[str] | None = None
    price: Decimal | None = Field(None, ge=0)
    mrp: Decimal | None = Field(None, ge=0)
    cost_price: Decimal | None = Field(None, ge=0)
    stock: int = Field(0, ge=0)
    color: str | None = Field(None, max_length=100)
    size: str | None = Field(None, max_length=100)
    material: str | None = Field(None, max_length=255)
    weight: Decimal | None = Field(None, ge=0)
    dimensions: dict | None = None
    country_of_origin: str | None = Field(None, max_length=100)
    manufacturer: str | None = Field(None, max_length=255)
    manufacturer_address: str | None = None
    packer: str | None = Field(None, max_length=255)
    importer: str | None = Field(None, max_length=255)
    keywords: list[str] | None = None
    search_terms: list[str] | None = None
    tags: list[str] | None = None
    status: str = Field("draft", pattern="^(draft|active|archived)$")


class ProductUpdateRequest(BaseModel):
    """Request body for updating a product. All fields optional."""
    sku: str | None = Field(None, min_length=1, max_length=100)
    product_name: str | None = Field(None, min_length=1, max_length=500)
    brand: str | None = Field(None, max_length=255)
    category_id: UUID | None = None
    subcategory: str | None = Field(None, max_length=255)
    product_type: str | None = Field(None, max_length=255)
    description: str | None = None
    short_description: str | None = None
    bullet_points: list[str] | None = None
    price: Decimal | None = Field(None, ge=0)
    mrp: Decimal | None = Field(None, ge=0)
    cost_price: Decimal | None = Field(None, ge=0)
    stock: int | None = Field(None, ge=0)
    color: str | None = Field(None, max_length=100)
    size: str | None = Field(None, max_length=100)
    material: str | None = Field(None, max_length=255)
    weight: Decimal | None = Field(None, ge=0)
    dimensions: dict | None = None
    country_of_origin: str | None = Field(None, max_length=100)
    manufacturer: str | None = Field(None, max_length=255)
    manufacturer_address: str | None = None
    packer: str | None = Field(None, max_length=255)
    importer: str | None = Field(None, max_length=255)
    keywords: list[str] | None = None
    search_terms: list[str] | None = None
    tags: list[str] | None = None
    status: str | None = Field(None, pattern="^(draft|active|archived)$")


class ProductImageResponse(BaseModel):
    """Product image in API response."""
    id: UUID
    url: str
    filename: str
    image_type: str
    sort_order: int
    is_primary: bool
    is_ai_generated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    """Full product response with images."""
    id: UUID
    user_id: UUID
    sku: str
    product_name: str
    brand: str | None = None
    category_id: UUID | None = None
    subcategory: str | None = None
    product_type: str | None = None
    description: str | None = None
    short_description: str | None = None
    bullet_points: list[str] | None = None
    price: Decimal | None = None
    mrp: Decimal | None = None
    cost_price: Decimal | None = None
    stock: int = 0
    color: str | None = None
    size: str | None = None
    material: str | None = None
    weight: Decimal | None = None
    dimensions: dict | None = None
    country_of_origin: str | None = None
    manufacturer: str | None = None
    manufacturer_address: str | None = None
    packer: str | None = None
    importer: str | None = None
    keywords: list[str] | None = None
    search_terms: list[str] | None = None
    tags: list[str] | None = None
    status: str
    images: list[ProductImageResponse] = []
    listing_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Paginated product list response."""
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
