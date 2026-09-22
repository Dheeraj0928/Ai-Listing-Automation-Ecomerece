"""Reference import service — orchestrates scraping, AI extraction, and listing creation."""

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIGenerationResult
from app.ai.prompts import (
    REFERENCE_IMPORT_SYSTEM_PROMPT,
    build_keyword_product_search_prompt,
    build_listing_from_reference_prompt,
    build_reference_extraction_prompt,
)
from app.models.ai_generation import AIGeneration
from app.models.marketplace_listing import MarketplaceListing
from app.models.product import Product
from app.services.ai_service import get_ai_provider
from app.services.scraper_service import ScraperService

logger = logging.getLogger(__name__)


class ReferenceImportService:
    """Handles importing product listings from competitor URLs or AI keyword suggestions."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.scraper = ScraperService()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _track_generation(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID | None,
        generation_type: str,
        result: AIGenerationResult,
        input_data: dict | None = None,
    ) -> AIGeneration:
        """Persist AI generation record for audit trail."""
        gen = AIGeneration(
            user_id=user_id,
            product_id=product_id,
            generation_type=generation_type,
            ai_provider=result.provider,
            ai_model=result.model,
            input_data=input_data or {},
            output_data=result.content if isinstance(result.content, dict) else {"text": result.content},
            status="completed",
            confidence_score=result.confidence_score,
            tokens_used=result.tokens_used,
            cost_estimate=result.cost_estimate,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        self.db.add(gen)
        await self.db.flush()
        await self.db.refresh(gen)
        return gen

    async def _get_seller_context(self, user_id: uuid.UUID, marketplace: str | None = None) -> str:
        """Build seller context string from their stored memory entries."""
        from sqlalchemy import select, or_
        from app.models.seller_memory import SellerMemory

        filters = [
            SellerMemory.user_id == user_id,
            SellerMemory.is_active.is_(True),
        ]
        if marketplace:
            filters.append(
                or_(
                    SellerMemory.scope == "global",
                    (SellerMemory.scope == "marketplace") & (SellerMemory.marketplace == marketplace),
                )
            )
        else:
            filters.append(SellerMemory.scope == "global")

        result = await self.db.execute(
            select(SellerMemory)
            .where(*filters)
            .order_by(SellerMemory.priority.desc())
            .limit(20)
        )
        memories = list(result.scalars().all())

        if not memories:
            return ""

        return "\n".join(f"- {mem.field_name}: {mem.field_value}" for mem in memories)

    def _create_product_from_data(
        self,
        user_id: uuid.UUID,
        ref_data: dict,
        sku: str | None = None,
        price: float | None = None,
        stock: int = 0,
    ) -> Product:
        """Create a Product model instance from extracted reference data."""
        # Auto-generate SKU if not provided
        if not sku:
            short_id = str(uuid.uuid4())[:8].upper()
            sku = f"REF-{short_id}"

        product = Product(
            user_id=user_id,
            sku=sku,
            product_name=ref_data.get("product_name", "Imported Product"),
            brand=ref_data.get("brand"),
            subcategory=ref_data.get("subcategory"),
            product_type=ref_data.get("product_type"),
            description=ref_data.get("description"),
            bullet_points=ref_data.get("bullet_points", []),
            price=Decimal(str(price)) if price else (Decimal(str(ref_data["price"])) if ref_data.get("price") else None),
            mrp=Decimal(str(ref_data["mrp"])) if ref_data.get("mrp") else None,
            stock=stock,
            color=ref_data.get("color"),
            size=ref_data.get("size"),
            material=ref_data.get("material"),
            country_of_origin=ref_data.get("country_of_origin"),
            manufacturer=ref_data.get("manufacturer"),
            keywords=ref_data.get("search_keywords", []),
            search_terms=ref_data.get("search_keywords", []),
            status="draft",
        )

        # Parse weight if string
        weight_val = ref_data.get("weight")
        if weight_val and isinstance(weight_val, str):
            import re
            weight_match = re.search(r"[\d.]+", weight_val)
            if weight_match:
                try:
                    product.weight = Decimal(weight_match.group())
                except Exception:
                    pass
        elif weight_val:
            try:
                product.weight = Decimal(str(weight_val))
            except Exception:
                pass

        # Parse dimensions
        dims = ref_data.get("dimensions")
        if dims and isinstance(dims, dict):
            product.dimensions = dims

        return product

    def _create_listing_from_ai(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        marketplace: str,
        ai_output: dict,
        product: Product,
    ) -> MarketplaceListing:
        """Create a MarketplaceListing from AI-generated listing content."""
        listing_data = {
            "title": ai_output.get("title") or product.product_name,
            "description": ai_output.get("description") or product.description or "",
            "bullet_points": ai_output.get("bullet_points") or product.bullet_points or [],
            "brand": product.brand or "",
            "price": float(product.price) if product.price else 0,
            "mrp": float(product.mrp) if product.mrp else 0,
            "color": product.color or "",
            "size": product.size or "",
            "material": product.material or "",
            "weight": float(product.weight) if product.weight else None,
            "country_of_origin": product.country_of_origin or "India",
            "manufacturer": product.manufacturer or "",
            "search_terms": ai_output.get("search_terms") or product.search_terms or [],
            "keywords": ai_output.get("backend_keywords", "").split() if ai_output.get("backend_keywords") else [],
            "sku": product.sku,
            "predicted_category": ai_output.get("predicted_category", ""),
            "seo_score": ai_output.get("seo_score", 0),
            "quality_score": ai_output.get("quality_score", 0),
        }

        # Marketplace-specific field names
        if marketplace == "flipkart":
            listing_data["key_features"] = listing_data.pop("bullet_points", [])

        return MarketplaceListing(
            product_id=product_id,
            user_id=user_id,
            marketplace=marketplace,
            status="ai_generated",
            listing_data=listing_data,
            marketplace_specific_data={
                "attributes": ai_output.get("attributes", {}),
            },
            version=1,
        )

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def import_from_url(
        self,
        user_id: uuid.UUID,
        url: str,
        marketplace: str = "flipkart",
        tone: str = "professional",
        provider_name: str | None = None,
        sku: str | None = None,
        price: float | None = None,
        stock: int = 0,
    ) -> dict:
        """
        Import a product listing from a competitor URL.

        Flow: Scrape URL → AI extract attributes → AI generate original listing → Create Product + Listing
        """
        # Step 1: Scrape the competitor page
        scraped_data = await self.scraper.scrape_product_url(url)
        logger.info(f"Scraped product from {scraped_data['source']}: {scraped_data.get('title', 'unknown')[:60]}")

        # Step 2: AI extract structured attributes from scraped content
        raw_text = scraped_data.get("raw_text", "")
        if not raw_text and scraped_data.get("title"):
            # Build raw_text from available fields
            parts = [scraped_data.get("title", "")]
            if scraped_data.get("bullet_points"):
                parts.extend(scraped_data["bullet_points"])
            if scraped_data.get("description"):
                parts.append(scraped_data["description"])
            if scraped_data.get("specifications"):
                parts.extend(f"{k}: {v}" for k, v in scraped_data["specifications"].items())
            raw_text = "\n".join(parts)

        extraction_prompt = build_reference_extraction_prompt(
            scraped_text=raw_text,
            source_url=url,
            marketplace=scraped_data["source"],
        )

        provider = get_ai_provider(provider_name)
        extraction_result = await provider.generate_json(
            extraction_prompt, system_prompt=REFERENCE_IMPORT_SYSTEM_PROMPT
        )
        extracted = extraction_result.content if isinstance(extraction_result.content, dict) else {}

        # Merge scraped data with AI-extracted data (AI takes priority for structured fields)
        merged_data = {**scraped_data, **extracted}
        if not merged_data.get("product_name") and scraped_data.get("title"):
            merged_data["product_name"] = scraped_data["title"]

        # Step 3: AI generate original listing content from extracted reference
        seller_context = await self._get_seller_context(user_id, marketplace)
        listing_prompt = build_listing_from_reference_prompt(
            reference_data=merged_data,
            marketplace=marketplace,
            tone=tone,
            seller_context=seller_context or None,
        )
        listing_result = await provider.generate_json(
            listing_prompt, system_prompt=REFERENCE_IMPORT_SYSTEM_PROMPT
        )
        ai_listing = listing_result.content if isinstance(listing_result.content, dict) else {}

        # Step 4: Create Product record
        product = self._create_product_from_data(
            user_id=user_id,
            ref_data=merged_data,
            sku=sku,
            price=price,
            stock=stock,
        )
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)

        # Step 5: Create MarketplaceListing record
        listing = self._create_listing_from_ai(
            user_id=user_id,
            product_id=product.id,
            marketplace=marketplace,
            ai_output=ai_listing,
            product=product,
        )
        self.db.add(listing)
        await self.db.flush()
        await self.db.refresh(listing)

        # Step 6: Track AI generations for audit
        await self._track_generation(
            user_id=user_id,
            product_id=product.id,
            generation_type="reference_extraction",
            result=extraction_result,
            input_data={"url": url, "source": scraped_data["source"]},
        )
        await self._track_generation(
            user_id=user_id,
            product_id=product.id,
            generation_type="reference_listing",
            result=listing_result,
            input_data={"marketplace": marketplace, "tone": tone, "source_url": url},
        )

        return {
            "product": product,
            "listing": listing,
            "extracted_attributes": merged_data,
            "ai_listing": ai_listing,
            "source_info": {
                "url": url,
                "marketplace": scraped_data["source"],
                "scraped_title": scraped_data.get("title", ""),
            },
        }

    async def import_from_keyword(
        self,
        user_id: uuid.UUID,
        keyword: str,
        marketplace: str = "flipkart",
        tone: str = "professional",
        provider_name: str | None = None,
    ) -> dict:
        """
        Generate product suggestions from a keyword using AI.

        Returns suggestions for the user to review and approve before creating a product.
        """
        prompt = build_keyword_product_search_prompt(
            keyword=keyword,
            marketplace=marketplace,
            tone=tone,
        )

        provider = get_ai_provider(provider_name)
        result = await provider.generate_json(
            prompt, system_prompt=REFERENCE_IMPORT_SYSTEM_PROMPT
        )

        output = result.content if isinstance(result.content, dict) else {}

        # Track the generation
        await self._track_generation(
            user_id=user_id,
            product_id=None,
            generation_type="keyword_search",
            result=result,
            input_data={"keyword": keyword, "marketplace": marketplace, "tone": tone},
        )

        return {
            "suggestions": output.get("suggestions", []),
            "keyword_analysis": output.get("keyword_analysis", {}),
            "keyword": keyword,
            "marketplace": marketplace,
            "generation_id": None,
        }

    async def confirm_keyword_import(
        self,
        user_id: uuid.UUID,
        suggestion: dict,
        marketplace: str = "flipkart",
        tone: str = "professional",
        provider_name: str | None = None,
        sku: str | None = None,
        price: float | None = None,
        stock: int = 0,
    ) -> dict:
        """
        Confirm a keyword suggestion and create Product + MarketplaceListing.

        The suggestion dict is one of the items returned from import_from_keyword().
        """
        # Step 1: Generate original listing from the suggestion data
        seller_context = await self._get_seller_context(user_id, marketplace)
        listing_prompt = build_listing_from_reference_prompt(
            reference_data=suggestion,
            marketplace=marketplace,
            tone=tone,
            seller_context=seller_context or None,
        )

        provider = get_ai_provider(provider_name)
        listing_result = await provider.generate_json(
            listing_prompt, system_prompt=REFERENCE_IMPORT_SYSTEM_PROMPT
        )
        ai_listing = listing_result.content if isinstance(listing_result.content, dict) else {}

        # Step 2: Use price from suggestion if not provided
        if price is None:
            price_range = suggestion.get("suggested_price_range", {})
            if price_range and price_range.get("max"):
                price = float(price_range.get("min", 0) + price_range.get("max", 0)) / 2

        # Step 3: Create Product
        product = self._create_product_from_data(
            user_id=user_id,
            ref_data=suggestion,
            sku=sku,
            price=price,
            stock=stock,
        )
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)

        # Step 4: Create MarketplaceListing
        listing = self._create_listing_from_ai(
            user_id=user_id,
            product_id=product.id,
            marketplace=marketplace,
            ai_output=ai_listing,
            product=product,
        )
        self.db.add(listing)
        await self.db.flush()
        await self.db.refresh(listing)

        # Step 5: Track generation
        await self._track_generation(
            user_id=user_id,
            product_id=product.id,
            generation_type="keyword_confirm_listing",
            result=listing_result,
            input_data={
                "marketplace": marketplace,
                "tone": tone,
                "suggestion_name": suggestion.get("product_name", ""),
            },
        )

        return {
            "product": product,
            "listing": listing,
            "ai_listing": ai_listing,
            "source_info": {
                "type": "keyword",
                "suggestion_name": suggestion.get("product_name", ""),
            },
        }
