"""AI generation API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.ai import (
    AIAnalyzeImageRequest,
    AIExtractAttributesRequest,
    AIGenerateBulletsRequest,
    AIGenerateDescriptionRequest,
    AIGenerateFullListingRequest,
    AIGenerateSearchTermsRequest,
    AIGenerateTitleRequest,
    AIGenerationResponse,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Generation"])


def _get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    return AIService(db)


@router.post("/generate-title", summary="Generate SEO-optimized product title")
async def generate_title(
    body: AIGenerateTitleRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(_get_ai_service),
):
    result = await ai_service.generate_title(
        user_id=user.id,
        product_id=body.product_id,
        marketplace=body.marketplace,
        tone=body.tone.value,
        provider_name=body.provider.value if body.provider else None,
    )
    return {"status": "success", "data": result}


@router.post("/generate-bullets", summary="Generate product bullet points")
async def generate_bullets(
    body: AIGenerateBulletsRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(_get_ai_service),
):
    result = await ai_service.generate_bullets(
        user_id=user.id,
        product_id=body.product_id,
        marketplace=body.marketplace,
        tone=body.tone.value,
        provider_name=body.provider.value if body.provider else None,
    )
    return {"status": "success", "data": result}


@router.post("/generate-description", summary="Generate product description")
async def generate_description(
    body: AIGenerateDescriptionRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(_get_ai_service),
):
    result = await ai_service.generate_description(
        user_id=user.id,
        product_id=body.product_id,
        marketplace=body.marketplace,
        tone=body.tone.value,
        provider_name=body.provider.value if body.provider else None,
    )
    return {"status": "success", "data": result}


@router.post("/generate-search-terms", summary="Generate search terms & backend keywords")
async def generate_search_terms(
    body: AIGenerateSearchTermsRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(_get_ai_service),
):
    result = await ai_service.generate_search_terms(
        user_id=user.id,
        product_id=body.product_id,
        marketplace=body.marketplace,
        provider_name=body.provider.value if body.provider else None,
    )
    return {"status": "success", "data": result}


@router.post("/extract-attributes", summary="Extract product attributes via AI")
async def extract_attributes(
    body: AIExtractAttributesRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(_get_ai_service),
):
    result = await ai_service.extract_attributes(
        user_id=user.id,
        product_id=body.product_id,
        provider_name=body.provider.value if body.provider else None,
    )
    return {"status": "success", "data": result}


@router.post("/analyze-image", summary="Analyze product image for Product DNA")
async def analyze_image(
    body: AIAnalyzeImageRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(_get_ai_service),
):
    result = await ai_service.analyze_product_image(
        user_id=user.id,
        product_id=body.product_id,
        image_url=body.image_url,
        provider_name=body.provider.value if body.provider else None,
    )
    return {"status": "success", "data": result}


@router.post("/generate-full-listing", summary="Generate complete listing (title + bullets + description + keywords)")
async def generate_full_listing(
    body: AIGenerateFullListingRequest,
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(_get_ai_service),
):
    result = await ai_service.generate_full_listing(
        user_id=user.id,
        product_id=body.product_id,
        marketplace=body.marketplace,
        tone=body.tone.value,
        provider_name=body.provider.value if body.provider else None,
    )
    return {"status": "success", "data": result}


@router.get("/generations", summary="List AI generation history")
async def list_generations(
    product_id: uuid.UUID | None = Query(default=None),
    generation_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    ai_service: AIService = Depends(_get_ai_service),
):
    result = await ai_service.get_generation_history(
        user_id=user.id,
        product_id=product_id,
        generation_type=generation_type,
        page=page,
        page_size=page_size,
    )

    # Serialize the ORM objects
    generations = [
        AIGenerationResponse.model_validate(gen)
        for gen in result["generations"]
    ]

    return {
        "status": "success",
        "data": {
            "generations": [g.model_dump() for g in generations],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
        },
    }
