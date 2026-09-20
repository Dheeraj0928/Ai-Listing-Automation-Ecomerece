"""Mock AI provider for development and testing without burning API credits."""

import json
import random
import logging

from app.ai.base import AIGenerationResult, AIProvider

logger = logging.getLogger(__name__)


class MockProvider(AIProvider):
    """Returns realistic-looking mock data for local development."""

    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: str = "text",
    ) -> AIGenerationResult:
        logger.info("[MockProvider] generate_text called")
        return AIGenerationResult(
            content="[MOCK] This is a mock AI generated text response for development purposes.",
            provider=self.provider_name,
            model="mock-v1",
            tokens_used=random.randint(50, 200),
            cost_estimate=0.0,
            confidence_score=0.95,
        )

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AIGenerationResult:
        logger.info("[MockProvider] generate_json called")

        # Try to figure out what kind of generation is being requested
        prompt_lower = prompt.lower()

        if "title" in prompt_lower:
            mock_data = {
                "title": "Premium Stainless Steel Water Bottle 1L – BPA Free, Leak-Proof, Double Wall Vacuum Insulated – Hot & Cold 24 Hours",
                "alternatives": [
                    "Insulated Steel Water Bottle 1 Litre – BPA Free Double Wall Flask for Gym, Office & Travel",
                    "1000ml Stainless Steel Thermos Flask – Vacuum Insulated, Leak Proof, Premium Quality",
                ],
                "seo_score": 92,
            }
        elif "bullet" in prompt_lower or "feature" in prompt_lower:
            mock_data = {
                "bullet_points": [
                    "🔥 DOUBLE WALL VACUUM INSULATION – Keeps beverages hot for 12 hours and cold for 24 hours, perfect for all seasons",
                    "💧 100% BPA-FREE & FOOD-GRADE – Made from premium 304 stainless steel, safe for daily hydration",
                    "🚫 LEAK-PROOF DESIGN – Advanced silicone seal cap ensures zero spills, ideal for gym, office, travel & outdoor",
                    "🎨 SLEEK & ERGONOMIC – Slim profile fits most car cup holders, powder-coated matte finish for a premium feel",
                    "✅ EASY TO CLEAN – Wide mouth opening allows thorough cleaning and adding ice cubes effortlessly",
                ],
                "quality_score": 88,
            }
        elif "search" in prompt_lower or "keyword" in prompt_lower:
            mock_data = {
                "search_terms": [
                    "stainless steel water bottle",
                    "vacuum insulated flask",
                    "BPA free water bottle 1 litre",
                    "thermos flask hot cold",
                    "gym water bottle steel",
                ],
                "backend_keywords": "water bottle stainless steel insulated flask thermos BPA free leak proof 1L gym office travel hot cold",
            }
        elif "description" in prompt_lower:
            mock_data = {
                "description": "Upgrade your hydration game with our Premium Stainless Steel Water Bottle. Crafted from food-grade 304 stainless steel with double-wall vacuum insulation technology, this bottle keeps your drinks hot for 12 hours and cold for 24 hours. The leak-proof design with an advanced silicone seal makes it the perfect companion for gym, office, travel, and outdoor adventures. With a sleek powder-coated matte finish and ergonomic design that fits most cup holders, this bottle combines style with functionality. BPA-free, eco-friendly, and built to last – make the sustainable choice today.",
                "word_count": 89,
            }
        elif "attribute" in prompt_lower or "dna" in prompt_lower:
            mock_data = {
                "brand": "AquaPure",
                "material": "Stainless Steel (304 Grade)",
                "color": "Midnight Black",
                "capacity": "1000 ml / 1 Litre",
                "weight": "350g",
                "dimensions": {"length": "28cm", "diameter": "7.5cm"},
                "detected_product_type": "Water Bottle / Flask",
                "key_features": ["Vacuum Insulated", "BPA Free", "Leak Proof", "Double Wall"],
            }
        else:
            mock_data = {
                "result": "[MOCK] Generated content",
                "quality_score": 85,
            }

        return AIGenerationResult(
            content=mock_data,
            provider=self.provider_name,
            model="mock-v1",
            tokens_used=random.randint(100, 500),
            cost_estimate=0.0,
            confidence_score=0.95,
        )

    async def analyze_image(
        self,
        image_url_or_base64: str,
        prompt: str,
        max_tokens: int = 4096,
    ) -> AIGenerationResult:
        logger.info("[MockProvider] analyze_image called")
        return AIGenerationResult(
            content={
                "shapes": ["cylindrical", "elongated"],
                "dominant_colors": ["#1a1a2e", "#16213e", "#0f3460"],
                "material_appearance": "Metallic / Matte powder-coated",
                "detected_product_type": "Water Bottle / Flask",
                "visible_components": ["body", "cap", "silicone seal", "brand logo"],
                "approximate_dimensions": {"height": "28cm", "diameter": "7.5cm"},
                "packaging_characteristics": ["retail box", "protective wrap"],
                "visual_features": ["matte finish", "ergonomic grip", "narrow mouth"],
            },
            provider=self.provider_name,
            model="mock-v1",
            tokens_used=random.randint(200, 600),
            cost_estimate=0.0,
            confidence_score=0.92,
        )
