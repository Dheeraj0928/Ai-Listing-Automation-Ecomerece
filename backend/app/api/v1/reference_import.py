"""Smart Reference Import API endpoints — import listings from URLs or keywords."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import AppException
from app.models.user import User
from app.schemas.reference_import import (
    KeywordConfirmRequest,
    KeywordSearchRequest,
    KeywordSearchResponse,
    ReferenceImportResponse,
    ReferenceURLImportRequest,
    ProductSummaryResponse,
    ListingSummaryResponse,
)
from app.services.reference_import_service import ReferenceImportService
from app.services.scraper_service import ScraperError

router = APIRouter(prefix="/reference-import", tags=["Smart Reference Import"])


def _get_service(db: AsyncSession = Depends(get_db)) -> ReferenceImportService:
    return ReferenceImportService(db)


@router.post(
    "/from-url",
    response_model=ReferenceImportResponse,
    summary="Import listing from competitor URL",
    description=(
        "Paste a competitor product URL (Amazon, Flipkart, Meesho). "
        "The system will scrape the page, extract attributes using AI, "
        "and generate an original, SEO-optimized listing draft. "
        "A Product (draft) and MarketplaceListing (ai_generated) will be created automatically."
    ),
)
async def import_from_url(
    body: ReferenceURLImportRequest,
    user: User = Depends(get_current_user),
    svc: ReferenceImportService = Depends(_get_service),
):
    try:
        result = await svc.import_from_url(
            user_id=user.id,
            url=body.url,
            marketplace=body.marketplace,
            tone=body.tone,
            provider_name=body.provider,
            sku=body.sku,
            price=body.price,
            stock=body.stock,
        )
    except ScraperError as e:
        raise AppException(
            message=f"Failed to scrape URL: {str(e)}",
            status_code=422,
            details={"url": body.url},
        )

    return ReferenceImportResponse(
        status="success",
        product=ProductSummaryResponse.model_validate(result["product"]),
        listing=ListingSummaryResponse.model_validate(result["listing"]),
        extracted_attributes=result.get("extracted_attributes"),
        ai_listing=result.get("ai_listing"),
        source_info=result.get("source_info"),
    )


@router.post(
    "/from-keyword",
    response_model=KeywordSearchResponse,
    summary="Search product suggestions by keyword",
    description=(
        "Type a product keyword like 'Red bicycle tail light' or 'Bluetooth earbuds'. "
        "AI will generate 3 product suggestions with complete attributes, pricing guidance, "
        "and SEO-optimized content. Review the suggestions and confirm your choice using the /confirm endpoint."
    ),
)
async def import_from_keyword(
    body: KeywordSearchRequest,
    user: User = Depends(get_current_user),
    svc: ReferenceImportService = Depends(_get_service),
):
    result = await svc.import_from_keyword(
        user_id=user.id,
        keyword=body.keyword,
        marketplace=body.marketplace,
        tone=body.tone,
        provider_name=body.provider,
    )

    return KeywordSearchResponse(
        status="success",
        keyword=result["keyword"],
        marketplace=result["marketplace"],
        suggestions=result["suggestions"],
        keyword_analysis=result.get("keyword_analysis"),
    )


@router.post(
    "/confirm",
    response_model=ReferenceImportResponse,
    summary="Confirm keyword suggestion & create product + listing",
    description=(
        "After reviewing keyword suggestions, select one and send it here. "
        "The system will generate a complete original listing and create both "
        "a Product (draft) and MarketplaceListing (ai_generated) record."
    ),
)
async def confirm_keyword_import(
    body: KeywordConfirmRequest,
    user: User = Depends(get_current_user),
    svc: ReferenceImportService = Depends(_get_service),
):
    result = await svc.confirm_keyword_import(
        user_id=user.id,
        suggestion=body.suggestion,
        marketplace=body.marketplace,
        tone=body.tone,
        provider_name=body.provider,
        sku=body.sku,
        price=body.price,
        stock=body.stock,
    )

    return ReferenceImportResponse(
        status="success",
        product=ProductSummaryResponse.model_validate(result["product"]),
        listing=ListingSummaryResponse.model_validate(result["listing"]),
        ai_listing=result.get("ai_listing"),
        source_info=result.get("source_info"),
    )
