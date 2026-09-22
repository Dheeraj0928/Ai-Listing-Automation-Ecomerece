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
        elif "reference" in prompt_lower or "scraped" in prompt_lower:
            mock_data = {
                "product_name": "USB Rechargeable LED Bicycle Tail Light - Waterproof IPX4, 4 Modes, Red Safety Warning Lamp",
                "brand": "CycleBright",
                "category": "Sports & Fitness",
                "subcategory": "Cycling Accessories",
                "product_type": "Bicycle Tail Light / Safety Light",
                "description": "High-visibility USB rechargeable LED tail light designed for cyclists. Features 4 lighting modes including steady, flash, strobe, and pulse. IPX4 waterproof rating ensures reliable performance in rain. Easy tool-free mounting on seat post or handlebar. Built-in 500mAh lithium battery provides up to 12 hours of runtime on a single charge.",
                "bullet_points": [
                    "USB Rechargeable — Built-in 500mAh battery, charges via micro-USB in just 2 hours",
                    "4 Light Modes — Steady, Flash, Strobe, and Pulse for maximum visibility",
                    "IPX4 Waterproof — Ride confidently in rain and harsh weather conditions",
                    "Easy Installation — Tool-free clip mount fits any seat post, handlebar, or backpack",
                    "Super Bright LED — 120 lumens with 180° wide-angle visibility for night safety",
                ],
                "price": 299.00,
                "mrp": 599.00,
                "color": "Red / Black",
                "size": "Compact (6.5 x 3.5 x 2.5 cm)",
                "material": "ABS Plastic + Polycarbonate Lens",
                "weight": "28g",
                "dimensions": {"length": "6.5", "width": "3.5", "height": "2.5", "unit": "cm"},
                "specifications": {
                    "Battery": "500mAh Lithium-ion",
                    "Charging": "Micro-USB",
                    "Lumens": "120",
                    "Waterproof Rating": "IPX4",
                    "Runtime": "Up to 12 hours",
                    "LED Type": "COB LED",
                },
                "key_features": ["USB Rechargeable", "4 Modes", "IPX4 Waterproof", "Tool-free Mount", "COB LED"],
                "country_of_origin": "China",
                "manufacturer": "Shenzhen Bright Tech Co.",
                "target_audience": "Cyclists, Bike Commuters, Night Riders",
                "use_cases": ["Night Cycling", "Road Safety", "Mountain Biking", "Urban Commuting"],
                "image_urls": [],
                "search_keywords": ["bicycle tail light", "bike rear light", "USB rechargeable cycle light", "LED safety light cycling", "waterproof bike light"],
            }
        elif "keyword" in prompt_lower and "suggestion" in prompt_lower or "seller wants to list" in prompt_lower:
            mock_data = {
                "suggestions": [
                    {
                        "product_name": "USB Rechargeable LED Bicycle Tail Light – IPX4 Waterproof, 4 Modes, Red Safety Warning",
                        "brand": "Generic",
                        "category": "Sports & Fitness",
                        "subcategory": "Cycling Accessories",
                        "product_type": "Bicycle Tail Light",
                        "description": "Stay safe during night rides with this high-visibility USB rechargeable LED bicycle tail light. Featuring 4 lighting modes and IPX4 waterproof rating, this compact safety light ensures you are visible to motorists from up to 200 meters away. The tool-free clip mount makes installation effortless on any seat post or backpack strap.",
                        "bullet_points": [
                            "🔋 USB RECHARGEABLE — Built-in 500mAh battery, full charge in 2 hours, lasts up to 12 hours",
                            "💡 4 LIGHT MODES — Steady, Flash, Strobe, Pulse for all riding conditions",
                            "🌧️ IPX4 WATERPROOF — Reliable in rain, dust, and rough terrain",
                            "🔧 EASY MOUNT — Tool-free clip attaches to seat post, handlebar, or backpack",
                            "🔴 SUPER BRIGHT — 120 lumens COB LED with 180° wide-angle beam",
                        ],
                        "suggested_price_range": {"min": 199, "max": 399, "currency": "INR"},
                        "color": "Red / Black",
                        "size": "Compact",
                        "material": "ABS Plastic",
                        "weight": "28g",
                        "dimensions": {"length": "6.5", "width": "3.5", "height": "2.5", "unit": "cm"},
                        "specifications": {"Battery": "500mAh", "Lumens": "120", "Waterproof": "IPX4"},
                        "key_features": ["USB Rechargeable", "4 Modes", "IPX4 Waterproof"],
                        "country_of_origin": "China",
                        "target_audience": "Cyclists, Commuters",
                        "use_cases": ["Night Cycling", "Road Safety"],
                        "search_keywords": ["bicycle tail light", "bike rear light", "cycle safety light"],
                        "confidence": 0.92,
                    },
                    {
                        "product_name": "Solar Powered Bicycle Red Warning Light – Auto On/Off, No Charging Required",
                        "brand": "Generic",
                        "category": "Sports & Fitness",
                        "subcategory": "Cycling Accessories",
                        "product_type": "Solar Bicycle Light",
                        "description": "Eco-friendly solar-powered bicycle warning light that charges automatically during daytime rides. No USB charging needed — the built-in solar panel keeps the battery topped up. Features auto on/off sensor that activates the red LED in low-light conditions.",
                        "bullet_points": [
                            "☀️ SOLAR POWERED — Never worry about charging, solar panel recharges automatically",
                            "🔴 AUTO ON/OFF — Light sensor activates in low-light conditions",
                            "🌧️ WEATHERPROOF — IPX5 rated for all-weather use",
                            "⚡ ENERGY EFFICIENT — Long-lasting red LED with minimal power consumption",
                            "📎 UNIVERSAL MOUNT — Fits all standard seat posts and bike racks",
                        ],
                        "suggested_price_range": {"min": 149, "max": 299, "currency": "INR"},
                        "color": "Red / Black",
                        "size": "Standard",
                        "material": "ABS + Solar Panel",
                        "weight": "35g",
                        "dimensions": {"length": "7", "width": "4", "height": "3", "unit": "cm"},
                        "specifications": {"Power": "Solar", "LED": "Red", "Waterproof": "IPX5"},
                        "key_features": ["Solar Powered", "Auto On/Off", "Weatherproof"],
                        "country_of_origin": "China",
                        "target_audience": "Eco-conscious Cyclists",
                        "use_cases": ["Daily Commuting", "Long Distance Cycling"],
                        "search_keywords": ["solar bicycle light", "auto bike light", "solar rear light"],
                        "confidence": 0.85,
                    },
                    {
                        "product_name": "Laser Beam Bicycle Safety Rear Light with Turn Signals – Remote Control, USB Rechargeable",
                        "brand": "Generic",
                        "category": "Sports & Fitness",
                        "subcategory": "Cycling Accessories",
                        "product_type": "Smart Bicycle Light with Turn Signals",
                        "description": "Advanced smart bicycle rear light with built-in laser lane projector and wireless turn signals. The wireless remote mounts on your handlebar, letting you signal left/right turns to traffic behind you. Features USB charging and 6 lighting modes.",
                        "bullet_points": [
                            "🚦 TURN SIGNALS — Wireless remote on handlebar for left/right turn indicators",
                            "🔴 LASER LANE — Projects laser bike lane lines on road for safe zone",
                            "🔋 USB RECHARGEABLE — 800mAh battery, 15+ hours runtime",
                            "💡 6 MODES — Including turn signals, steady, flash, and laser",
                            "📡 WIRELESS REMOTE — 50m range, easy thumb control while riding",
                        ],
                        "suggested_price_range": {"min": 499, "max": 899, "currency": "INR"},
                        "color": "Red / Black",
                        "size": "Medium",
                        "material": "ABS + Silicone",
                        "weight": "65g",
                        "dimensions": {"length": "9", "width": "5", "height": "3.5", "unit": "cm"},
                        "specifications": {"Battery": "800mAh", "Remote Range": "50m", "Laser": "Yes"},
                        "key_features": ["Turn Signals", "Laser Lane", "Wireless Remote"],
                        "country_of_origin": "China",
                        "target_audience": "Urban Cyclists, Safety-conscious Riders",
                        "use_cases": ["Urban Commuting", "Night Riding", "Traffic Safety"],
                        "search_keywords": ["laser bicycle light", "turn signal bike light", "smart cycle light"],
                        "confidence": 0.88,
                    },
                ],
                "keyword_analysis": {
                    "interpreted_as": "Red-colored bicycle/cycling safety tail light",
                    "product_category": "Cycling Accessories > Lights",
                    "market_segment": "Budget to Mid-range",
                },
            }
        elif "reference product data" in prompt_lower or "completely original" in prompt_lower:
            mock_data = {
                "title": "Ultra-Bright USB Rechargeable Bicycle Tail Light – 120 Lumens COB LED, 4 Modes, IPX4 Waterproof, Red Safety Warning Light for Night Cycling",
                "bullet_points": [
                    "🔋 LONG-LASTING USB RECHARGEABLE — Built-in 500mAh lithium battery delivers up to 12 hours of continuous illumination on a single 2-hour charge",
                    "💡 4 SMART LIGHTING MODES — Switch between Steady, Rapid Flash, Strobe, and Pulse modes to match your riding environment and visibility needs",
                    "🌧️ IPX4 WATERPROOF CERTIFIED — Engineered to perform flawlessly in rain, fog, and dusty trail conditions for year-round cycling safety",
                    "🔧 INSTANT TOOL-FREE INSTALLATION — Universal clip mount securely attaches to seat posts, handlebars, backpacks, and helmets in seconds",
                    "🔴 180° WIDE-ANGLE VISIBILITY — High-intensity 120-lumen COB LED chip ensures you're visible to motorists from up to 200 meters in all directions",
                ],
                "description": "Ride with confidence day and night with our Ultra-Bright USB Rechargeable Bicycle Tail Light. Engineered for serious cyclists who prioritize safety, this compact yet powerful rear light features a high-intensity 120-lumen COB LED chip that provides crystal-clear 180-degree visibility, ensuring motorists can spot you from up to 200 meters away.\n\nWith 4 intelligent lighting modes — Steady, Rapid Flash, Strobe, and Pulse — you can customize your visibility for any riding scenario, from busy city streets to dark country roads. The IPX4 waterproof certification means you never have to worry about sudden rain or muddy trails cutting your ride short.\n\nThe built-in 500mAh rechargeable lithium battery delivers an impressive 12 hours of runtime on a single charge, and the micro-USB port means you can top up from any power bank or laptop. Installation takes mere seconds with our tool-free universal clip mount that fits any seat post diameter, handlebar, backpack strap, or helmet vent.\n\nWeighing just 28 grams, this ultra-lightweight tail light adds virtually no weight to your setup while dramatically boosting your on-road safety. Whether you're a daily commuter, weekend warrior, or mountain trail enthusiast — make every ride a safe ride.",
                "search_terms": ["bicycle tail light", "bike rear light", "USB rechargeable cycle light", "LED bike safety light", "waterproof bicycle light", "red bike light", "cycling rear lamp", "night riding light", "COB LED tail light", "seat post light", "cycle safety lamp", "MTB rear light"],
                "backend_keywords": "bicycle tail light USB rechargeable LED red safety waterproof IPX4 COB rear lamp cycling night riding seat post clip mount 120 lumens",
                "predicted_category": "Sports, Fitness & Outdoors > Cycling > Lights & Reflectors > Tail Lights",
                "attributes": {
                    "brand": "",
                    "material": "ABS Plastic + Polycarbonate",
                    "color": "Red / Black",
                    "size": "Compact (6.5 x 3.5 x 2.5 cm)",
                    "weight": "28g",
                    "country_of_origin": "China",
                },
                "seo_score": 94,
                "quality_score": 91,
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
