"""Pydantic schemas for AI generation requests and responses."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class GenerationType(str, Enum):
    TITLE = "title"
    DESCRIPTION = "description"
    BULLETS = "bullets"
    SEARCH_TERMS = "search_terms"
    ATTRIBUTES = "attributes"
    IMAGE_ANALYSIS = "image_analysis"
    FULL_LISTING = "full_listing"


class ToneType(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    PREMIUM = "premium"
    LUXURY = "luxury"
    FUN = "fun"


class AIProviderType(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    MOCK = "mock"


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

class AIGenerateRequest(BaseModel):
    """Common request body for all AI generation endpoints."""

    product_id: uuid.UUID
    marketplace: str = Field(default="amazon", pattern="^(amazon|flipkart|meesho)$")
    tone: ToneType = ToneType.PROFESSIONAL
    provider: AIProviderType | None = None  # None = use default from config


class AIGenerateTitleRequest(AIGenerateRequest):
    pass


class AIGenerateBulletsRequest(AIGenerateRequest):
    count: int = Field(default=5, ge=3, le=7)


class AIGenerateDescriptionRequest(AIGenerateRequest):
    max_words: int = Field(default=250, ge=50, le=500)


class AIGenerateSearchTermsRequest(AIGenerateRequest):
    pass


class AIExtractAttributesRequest(BaseModel):
    product_id: uuid.UUID
    provider: AIProviderType | None = None


class AIAnalyzeImageRequest(BaseModel):
    product_id: uuid.UUID
    image_url: str | None = None  # If None, use primary product image
    provider: AIProviderType | None = None


class AIGenerateFullListingRequest(AIGenerateRequest):
    """Generate title + bullets + description + search terms in one shot."""
    pass


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

class AIGenerationResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID | None
    generation_type: str
    ai_provider: str
    ai_model: str
    status: str
    output_data: dict | None
    tokens_used: int | None
    cost_estimate: float | None
    confidence_score: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIGenerationListResponse(BaseModel):
    generations: list[AIGenerationResponse]
    total: int
    page: int
    page_size: int


class AITitleResponse(BaseModel):
    title: str
    alternatives: list[str] = []
    seo_score: int = 0
    keywords_used: list[str] = []
    generation_id: uuid.UUID


class AIBulletsResponse(BaseModel):
    bullet_points: list[str]
    quality_score: int = 0
    generation_id: uuid.UUID


class AIDescriptionResponse(BaseModel):
    description: str
    word_count: int = 0
    generation_id: uuid.UUID


class AISearchTermsResponse(BaseModel):
    search_terms: list[str]
    backend_keywords: str = ""
    long_tail_keywords: list[str] = []
    generation_id: uuid.UUID


class AIAttributesResponse(BaseModel):
    attributes: dict
    generation_id: uuid.UUID


class AIProductDNAResponse(BaseModel):
    dna: dict
    generation_id: uuid.UUID


class AIFullListingResponse(BaseModel):
    title: str
    bullet_points: list[str]
    description: str
    search_terms: list[str]
    backend_keywords: str = ""
    predicted_category: str = ""
    attributes: dict = {}
    seo_score: int = 0
    quality_score: int = 0
    generation_id: uuid.UUID
