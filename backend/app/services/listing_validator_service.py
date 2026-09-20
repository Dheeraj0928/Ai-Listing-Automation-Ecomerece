"""Listing validator service — validates listings against marketplace-specific rules."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.marketplace import get_marketplace_adapter
from app.models.marketplace_listing import MarketplaceListing
from app.repositories.listing_repo import ListingRepository
from app.schemas.listing import ListingValidateResponse


class ListingValidatorService:
    """Validate listings against marketplace rules."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.listing_repo = ListingRepository(db)

    async def validate_listing(
        self, user_id: uuid.UUID, listing_id: uuid.UUID
    ) -> ListingValidateResponse:
        """Validate a single listing against its marketplace rules."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if listing is None or listing.user_id != user_id:
            raise NotFoundError("Listing", str(listing_id))

        adapter = get_marketplace_adapter(listing.marketplace)
        result = await adapter.validate_listing(listing.listing_data or {})

        # Persist validation results on the listing
        listing.validation_results = {
            "is_valid": result.is_valid,
            "errors": [{"field": e.field, "message": e.message, "severity": e.severity} for e in result.errors],
            "warnings": [{"field": w.field, "message": w.message, "severity": w.severity} for w in result.warnings],
        }
        listing.completion_percentage = round(result.completion_percentage, 1)

        if result.is_valid:
            listing.status = "validated"
        else:
            listing.status = "needs_review"

        await self.db.flush()
        await self.db.refresh(listing)

        return ListingValidateResponse(
            is_valid=result.is_valid,
            completion_percentage=result.completion_percentage,
            errors=[{"field": e.field, "message": e.message} for e in result.errors],
            warnings=[{"field": w.field, "message": w.message} for w in result.warnings],
        )

    async def bulk_validate(
        self, user_id: uuid.UUID, listing_ids: list[uuid.UUID]
    ) -> list[dict]:
        """Validate multiple listings at once."""
        results = []
        for lid in listing_ids:
            try:
                result = await self.validate_listing(user_id, lid)
                results.append({
                    "listing_id": str(lid),
                    "is_valid": result.is_valid,
                    "completion_percentage": result.completion_percentage,
                    "error_count": len(result.errors),
                })
            except NotFoundError:
                results.append({
                    "listing_id": str(lid),
                    "is_valid": False,
                    "error": "Listing not found",
                })
        return results
