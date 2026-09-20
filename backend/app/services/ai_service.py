"""AI service — orchestrates AI providers, prompt building, and generation tracking."""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIProvider, AIGenerationResult
from app.ai.mock_provider import MockProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.prompts import (
    LISTING_SYSTEM_PROMPT,
    PRODUCT_DNA_SYSTEM_PROMPT,
    build_attribute_extraction_prompt,
    build_bullets_prompt,
    build_description_prompt,
    build_full_listing_prompt,
    build_image_analysis_prompt,
    build_search_terms_prompt,
    build_title_prompt,
)
from app.core.config import settings
from app.models.ai_generation import AIGeneration
from app.models.product import Product
from app.models.seller_memory import SellerMemory

logger = logging.getLogger(__name__)


def get_ai_provider(provider_name: str | None = None) -> AIProvider:
    """Factory function to instantiate the right AI provider."""
    name = (provider_name or settings.AI_PROVIDER).lower()

    if name == "openai":
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set, falling back to mock provider")
            return MockProvider()
        return OpenAIProvider()
    elif name == "gemini":
        if not settings.GOOGLE_AI_API_KEY:
            logger.warning("GOOGLE_AI_API_KEY not set, falling back to mock provider")
            return MockProvider()
        return GeminiProvider()
    else:
        return MockProvider()


class AIService:
    """High-level service that coordinates AI generation for e-commerce listings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _get_product(self, product_id: uuid.UUID, user_id: uuid.UUID) -> Product:
        from sqlalchemy import select
        result = await self.db.execute(
            select(Product).where(Product.id == product_id, Product.user_id == user_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise ValueError(f"Product {product_id} not found or access denied")
        return product

    async def _get_seller_context(self, user_id: uuid.UUID, marketplace: str | None = None) -> str:
        """Build seller context string from their stored memory entries."""
        from sqlalchemy import select

        filters = [
            SellerMemory.user_id == user_id,
            SellerMemory.is_active.is_(True),
        ]
        if marketplace:
            # Get global + marketplace-specific memories
            from sqlalchemy import or_
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

        lines = []
        for mem in memories:
            lines.append(f"- {mem.field_name}: {mem.field_value}")
        return "\n".join(lines)

    def _product_attributes(self, product: Product) -> dict:
        """Extract product attributes as a dict for prompt injection."""
        attrs = {}
        for field in ["brand", "color", "size", "material", "country_of_origin", "product_type"]:
            val = getattr(product, field, None)
            if val:
                attrs[field] = val
        if product.weight:
            attrs["weight"] = str(product.weight)
        if product.dimensions:
            attrs["dimensions"] = str(product.dimensions)
        return attrs

    async def _track_generation(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID | None,
        generation_type: str,
        result: AIGenerationResult,
        input_data: dict | None = None,
    ) -> AIGeneration:
        """Persist the AI generation record to the database for audit trail."""
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

    # ------------------------------------------------------------------
    # Public generation methods
    # ------------------------------------------------------------------

    async def generate_title(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        marketplace: str = "amazon",
        tone: str = "professional",
        provider_name: str | None = None,
    ) -> dict:
        product = await self._get_product(product_id, user_id)
        seller_context = await self._get_seller_context(user_id, marketplace)
        attributes = self._product_attributes(product)

        prompt = build_title_prompt(
            product_name=product.product_name,
            brand=product.brand,
            category=product.category.name if product.category else None,
            attributes=attributes,
            marketplace=marketplace,
            tone=tone,
            seller_context=seller_context or None,
        )

        provider = get_ai_provider(provider_name)
        result = await provider.generate_json(prompt, system_prompt=LISTING_SYSTEM_PROMPT)

        gen = await self._track_generation(
            user_id, product_id, "title", result,
            input_data={"marketplace": marketplace, "tone": tone},
        )

        output = result.content if isinstance(result.content, dict) else {}
        return {
            "title": output.get("title", ""),
            "alternatives": output.get("alternatives", []),
            "seo_score": output.get("seo_score", 0),
            "keywords_used": output.get("keywords_used", []),
            "generation_id": gen.id,
        }

    async def generate_bullets(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        marketplace: str = "amazon",
        tone: str = "professional",
        provider_name: str | None = None,
    ) -> dict:
        product = await self._get_product(product_id, user_id)
        seller_context = await self._get_seller_context(user_id, marketplace)
        attributes = self._product_attributes(product)

        prompt = build_bullets_prompt(
            product_name=product.product_name,
            brand=product.brand,
            description=product.description,
            attributes=attributes,
            marketplace=marketplace,
            tone=tone,
            seller_context=seller_context or None,
        )

        provider = get_ai_provider(provider_name)
        result = await provider.generate_json(prompt, system_prompt=LISTING_SYSTEM_PROMPT)

        gen = await self._track_generation(
            user_id, product_id, "bullets", result,
            input_data={"marketplace": marketplace, "tone": tone},
        )

        output = result.content if isinstance(result.content, dict) else {}
        return {
            "bullet_points": output.get("bullet_points", []),
            "quality_score": output.get("quality_score", 0),
            "generation_id": gen.id,
        }

    async def generate_description(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        marketplace: str = "amazon",
        tone: str = "professional",
        provider_name: str | None = None,
    ) -> dict:
        product = await self._get_product(product_id, user_id)
        seller_context = await self._get_seller_context(user_id, marketplace)
        attributes = self._product_attributes(product)
        bullet_points = product.bullet_points or []

        prompt = build_description_prompt(
            product_name=product.product_name,
            brand=product.brand,
            bullet_points=bullet_points,
            attributes=attributes,
            marketplace=marketplace,
            tone=tone,
            seller_context=seller_context or None,
        )

        provider = get_ai_provider(provider_name)
        result = await provider.generate_json(prompt, system_prompt=LISTING_SYSTEM_PROMPT)

        gen = await self._track_generation(
            user_id, product_id, "description", result,
            input_data={"marketplace": marketplace, "tone": tone},
        )

        output = result.content if isinstance(result.content, dict) else {}
        return {
            "description": output.get("description", ""),
            "word_count": output.get("word_count", 0),
            "generation_id": gen.id,
        }

    async def generate_search_terms(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        marketplace: str = "amazon",
        provider_name: str | None = None,
    ) -> dict:
        product = await self._get_product(product_id, user_id)
        attributes = self._product_attributes(product)

        prompt = build_search_terms_prompt(
            product_name=product.product_name,
            brand=product.brand,
            category=product.category.name if product.category else None,
            attributes=attributes,
            marketplace=marketplace,
        )

        provider = get_ai_provider(provider_name)
        result = await provider.generate_json(prompt, system_prompt=LISTING_SYSTEM_PROMPT)

        gen = await self._track_generation(
            user_id, product_id, "search_terms", result,
            input_data={"marketplace": marketplace},
        )

        output = result.content if isinstance(result.content, dict) else {}
        return {
            "search_terms": output.get("search_terms", []),
            "backend_keywords": output.get("backend_keywords", ""),
            "long_tail_keywords": output.get("long_tail_keywords", []),
            "generation_id": gen.id,
        }

    async def extract_attributes(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        provider_name: str | None = None,
    ) -> dict:
        product = await self._get_product(product_id, user_id)

        prompt = build_attribute_extraction_prompt(
            product_name=product.product_name,
            description=product.description,
            category=product.category.name if product.category else None,
        )

        provider = get_ai_provider(provider_name)
        result = await provider.generate_json(prompt, system_prompt=PRODUCT_DNA_SYSTEM_PROMPT)

        gen = await self._track_generation(
            user_id, product_id, "attributes", result,
        )

        output = result.content if isinstance(result.content, dict) else {}
        return {
            "attributes": output,
            "generation_id": gen.id,
        }

    async def analyze_product_image(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        image_url: str | None = None,
        provider_name: str | None = None,
    ) -> dict:
        product = await self._get_product(product_id, user_id)

        # If no image URL provided, try to use the primary product image
        if not image_url and product.images:
            primary_images = [img for img in product.images if img.is_primary]
            if primary_images:
                image_url = primary_images[0].url
            elif product.images:
                image_url = product.images[0].url

        if not image_url:
            raise ValueError("No image available for analysis. Upload a product image first.")

        prompt = build_image_analysis_prompt()
        provider = get_ai_provider(provider_name)
        result = await provider.analyze_image(image_url, prompt)

        gen = await self._track_generation(
            user_id, product_id, "image_analysis", result,
            input_data={"image_url": image_url},
        )

        # Also save as ProductDNA if successful
        output = result.content if isinstance(result.content, dict) else {}
        if output and "detected_product_type" in output:
            await self._save_product_dna(product_id, output, result)

        return {
            "dna": output,
            "generation_id": gen.id,
        }

    async def generate_full_listing(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        marketplace: str = "amazon",
        tone: str = "professional",
        provider_name: str | None = None,
    ) -> dict:
        product = await self._get_product(product_id, user_id)
        seller_context = await self._get_seller_context(user_id, marketplace)
        attributes = self._product_attributes(product)

        prompt = build_full_listing_prompt(
            product_name=product.product_name,
            brand=product.brand,
            category=product.category.name if product.category else None,
            description=product.description,
            attributes=attributes,
            marketplace=marketplace,
            tone=tone,
            seller_context=seller_context or None,
        )

        provider = get_ai_provider(provider_name)
        result = await provider.generate_json(prompt, system_prompt=LISTING_SYSTEM_PROMPT)

        gen = await self._track_generation(
            user_id, product_id, "full_listing", result,
            input_data={"marketplace": marketplace, "tone": tone},
        )

        output = result.content if isinstance(result.content, dict) else {}
        return {
            "title": output.get("title", ""),
            "bullet_points": output.get("bullet_points", []),
            "description": output.get("description", ""),
            "search_terms": output.get("search_terms", []),
            "backend_keywords": output.get("backend_keywords", ""),
            "predicted_category": output.get("predicted_category", ""),
            "attributes": output.get("attributes", {}),
            "seo_score": output.get("seo_score", 0),
            "quality_score": output.get("quality_score", 0),
            "generation_id": gen.id,
        }

    # ------------------------------------------------------------------
    # Generation history
    # ------------------------------------------------------------------

    async def get_generation_history(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        generation_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        from sqlalchemy import select, func

        filters = [AIGeneration.user_id == user_id]
        if product_id:
            filters.append(AIGeneration.product_id == product_id)
        if generation_type:
            filters.append(AIGeneration.generation_type == generation_type)

        # Count total
        count_q = select(func.count()).select_from(AIGeneration).where(*filters)
        total = (await self.db.execute(count_q)).scalar_one()

        # Fetch page
        offset = (page - 1) * page_size
        query = (
            select(AIGeneration)
            .where(*filters)
            .order_by(AIGeneration.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        generations = list(result.scalars().all())

        return {
            "generations": generations,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _save_product_dna(
        self,
        product_id: uuid.UUID,
        dna_data: dict,
        ai_result: AIGenerationResult,
    ) -> None:
        """Upsert Product DNA record from AI analysis results."""
        from sqlalchemy import select
        from app.models.product_dna import ProductDNA

        result = await self.db.execute(
            select(ProductDNA).where(ProductDNA.product_id == product_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.shapes = dna_data.get("shapes")
            existing.dominant_colors = dna_data.get("dominant_colors")
            existing.material_appearance = dna_data.get("material_appearance")
            existing.detected_product_type = dna_data.get("detected_product_type")
            existing.visible_components = dna_data.get("visible_components")
            existing.approximate_dimensions = dna_data.get("approximate_dimensions")
            existing.packaging_characteristics = dna_data.get("packaging_characteristics")
            existing.visual_features = dna_data.get("visual_features")
            existing.raw_analysis = str(dna_data)
            existing.ai_provider = ai_result.provider
            existing.ai_model = ai_result.model
            existing.confidence_score = ai_result.confidence_score
            existing.analyzed_at = datetime.now(timezone.utc)
        else:
            dna = ProductDNA(
                product_id=product_id,
                shapes=dna_data.get("shapes"),
                dominant_colors=dna_data.get("dominant_colors"),
                material_appearance=dna_data.get("material_appearance"),
                detected_product_type=dna_data.get("detected_product_type"),
                visible_components=dna_data.get("visible_components"),
                approximate_dimensions=dna_data.get("approximate_dimensions"),
                packaging_characteristics=dna_data.get("packaging_characteristics"),
                visual_features=dna_data.get("visual_features"),
                raw_analysis=str(dna_data),
                ai_provider=ai_result.provider,
                ai_model=ai_result.model,
                confidence_score=ai_result.confidence_score,
                analyzed_at=datetime.now(timezone.utc),
            )
            self.db.add(dna)

        await self.db.flush()
