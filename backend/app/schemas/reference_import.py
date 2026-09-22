"""Schemas for the Smart Reference Import feature."""

from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ReferenceURLImportRequest(BaseModel):
    """Request to import a product listing from a competitor URL."""
    url: str = Field(..., description="Competitor product URL (Amazon, Flipkart, Meesho)")
    marketplace: str = Field("flipkart", pattern="^(amazon|flipkart|meesho)$", description="Target marketplace for the listing")
    tone: str = Field("professional", pattern="^(professional|casual|luxury|technical)$")
    provider: str | None = Field(None, description="AI provider override")
    sku: str | None = Field(None, description="Custom SKU for the product (auto-generated if not provided)")
    price: float | None = Field(None, ge=0, description="Override price (uses scraped price if not provided)")
    stock: int = Field(0, ge=0, description="Initial stock quantity")


class KeywordSearchRequest(BaseModel):
    """Request to search for product suggestions by keyword."""
    keyword: str = Field(..., min_length=2, max_length=500, description="Product keyword or description, e.g. 'Red bicycle tail light'")
    marketplace: str = Field("flipkart", pattern="^(amazon|flipkart|meesho)$")
    tone: str = Field("professional", pattern="^(professional|casual|luxury|technical)$")
    provider: str | None = Field(None, description="AI provider override")


class KeywordConfirmRequest(BaseModel):
    """Request to confirm a keyword suggestion and create product + listing."""
    suggestion: dict = Field(..., description="The selected suggestion object from keyword search response")
    marketplace: str = Field("flipkart", pattern="^(amazon|flipkart|meesho)$")
    tone: str = Field("professional", pattern="^(professional|casual|luxury|technical)$")
    provider: str | None = Field(None, description="AI provider override")
    sku: str | None = Field(None, description="Custom SKU (auto-generated if not provided)")
    price: float | None = Field(None, ge=0, description="Selling price")
    stock: int = Field(0, ge=0, description="Initial stock quantity")


class SourceInfoResponse(BaseModel):
    """Information about the import source."""
    url: str | None = None
    marketplace: str | None = None
    scraped_title: str | None = None
    type: str | None = None
    suggestion_name: str | None = None


class ProductSummaryResponse(BaseModel):
    """Minimal product info in import response."""
    id: UUID
    sku: str
    product_name: str
    brand: str | None = None
    price: Decimal | None = None
    mrp: Decimal | None = None
    color: str | None = None
    material: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ListingSummaryResponse(BaseModel):
    """Minimal listing info in import response."""
    id: UUID
    product_id: UUID
    marketplace: str
    status: str
    listing_data: dict | None = None
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ReferenceImportResponse(BaseModel):
    """Response after importing from URL or confirming a keyword suggestion."""
    status: str = "success"
    product: ProductSummaryResponse
    listing: ListingSummaryResponse
    extracted_attributes: dict | None = None
    ai_listing: dict | None = None
    source_info: dict | None = None


class KeywordSuggestionItem(BaseModel):
    """A single product suggestion from keyword search."""
    product_name: str
    brand: str | None = None
    category: str | None = None
    subcategory: str | None = None
    product_type: str | None = None
    description: str | None = None
    bullet_points: list[str] = []
    suggested_price_range: dict | None = None
    color: str | None = None
    size: str | None = None
    material: str | None = None
    weight: str | None = None
    dimensions: dict | None = None
    specifications: dict | None = None
    key_features: list[str] = []
    country_of_origin: str | None = None
    target_audience: str | None = None
    use_cases: list[str] = []
    search_keywords: list[str] = []
    confidence: float = 0.0


class KeywordSearchResponse(BaseModel):
    """Response from keyword search with product suggestions."""
    status: str = "success"
    keyword: str
    marketplace: str
    suggestions: list[dict] = []
    keyword_analysis: dict | None = None
