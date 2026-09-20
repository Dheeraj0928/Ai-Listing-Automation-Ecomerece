"""Listing generator service — uses AI service to create marketplace-specific listings."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.marketplace_listing import MarketplaceListing
from app.models.product import Product
from app.repositories.audit_repo import AuditRepository
from app.repositories.listing_repo import ListingRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.listing import ListingResponse
from app.services.ai_service import AIService


class ListingGeneratorService:
    """Generate AI-powered listings for products across marketplaces."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.listing_repo = ListingRepository(db)
        self.audit_repo = AuditRepository(db)
        self.ai_service = AIService(db)

    async def generate_listings(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        marketplaces: list[str],
        tone: str = "professional",
        provider_name: str | None = None,
    ) -> list[ListingResponse]:
        """Generate listings for a product across multiple marketplaces."""
        # Verify product exists and belongs to user
        product = await self.product_repo.get_by_id(product_id)
        if product is None or product.user_id != user_id:
            raise NotFoundError("Product", str(product_id))

        results = []

        for marketplace in marketplaces:
            # Generate AI content
            ai_result = await self.ai_service.generate_full_listing(
                user_id=user_id,
                product_id=product_id,
                marketplace=marketplace,
                tone=tone,
                provider_name=provider_name,
            )

            # Build listing data from AI output
            listing_data = self._build_listing_data(product, ai_result, marketplace)

            # Create or update the listing record
            listing = await self._upsert_listing(
                user_id=user_id,
                product_id=product_id,
                marketplace=marketplace,
                listing_data=listing_data,
                ai_result=ai_result,
            )

            results.append(ListingResponse.model_validate(listing))

            await self.audit_repo.log_action(
                user_id=user_id,
                action="listing_generated",
                entity_type="listing",
                entity_id=listing.id,
                new_value={"marketplace": marketplace, "product_id": str(product_id)},
            )

        return results

    def _build_listing_data(self, product: Product, ai_result: dict, marketplace: str) -> dict:
        """Combine product data with AI-generated content into listing format."""
        output = ai_result.get("output", {})

        data = {
            "title": output.get("title") or product.product_name,
            "description": output.get("description") or product.description or "",
            "bullet_points": output.get("bullet_points") or product.bullet_points or [],
            "brand": product.brand or "",
            "price": float(product.price) if product.price else 0,
            "mrp": float(product.mrp) if product.mrp else 0,
            "color": product.color or "",
            "size": product.size or "",
            "material": product.material or "",
            "weight": float(product.weight) if product.weight else None,
            "country_of_origin": product.country_of_origin or "India",
            "manufacturer": product.manufacturer or "",
            "search_terms": output.get("search_terms") or product.search_terms or [],
            "keywords": output.get("keywords") or product.keywords or [],
            "sku": product.sku,
        }

        # Marketplace-specific field names
        if marketplace == "flipkart":
            data["key_features"] = data.pop("bullet_points", [])
        elif marketplace == "meesho":
            # Meesho uses simpler format
            pass

        return data

    async def _upsert_listing(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        marketplace: str,
        listing_data: dict,
        ai_result: dict,
    ) -> MarketplaceListing:
        """Create a new listing or update an existing draft for the same product+marketplace."""
        from sqlalchemy import select

        # Check for existing draft/ai_generated listing
        result = await self.db.execute(
            select(MarketplaceListing).where(
                MarketplaceListing.product_id == product_id,
                MarketplaceListing.user_id == user_id,
                MarketplaceListing.marketplace == marketplace,
                MarketplaceListing.deleted_at.is_(None),
                MarketplaceListing.status.in_(["draft", "ai_generated", "needs_review"]),
            ).limit(1)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.listing_data = listing_data
            existing.status = "ai_generated"
            existing.version += 1
            existing.completion_percentage = None
            existing.error_message = None
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            listing = MarketplaceListing(
                product_id=product_id,
                user_id=user_id,
                marketplace=marketplace,
                status="ai_generated",
                listing_data=listing_data,
                version=1,
            )
            self.db.add(listing)
            await self.db.flush()
            await self.db.refresh(listing)
            return listing
