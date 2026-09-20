"""Prompt templates for e-commerce listing generation — the heart of the AI engine."""


# ---------------------------------------------------------------------------
# System Prompts
# ---------------------------------------------------------------------------


LISTING_SYSTEM_PROMPT = """You are an expert e-commerce listing copywriter and SEO specialist.
You create high-converting product listings for Indian and global marketplaces (Amazon, Flipkart, Meesho).
Your writing is professional, factual, keyword-rich, and follows marketplace best practices.

Key rules:
- Never use false claims or exaggerated superlatives
- Always use natural, search-friendly language
- Include relevant Hindi transliterations only when explicitly requested
- Follow marketplace character limits strictly
- Write in the tone requested by the seller (Professional / Casual / Premium / Luxury)
"""

PRODUCT_DNA_SYSTEM_PROMPT = """You are a product analysis AI.
Given product information (text and/or images), extract structured product DNA.
Return ONLY valid JSON with no additional text or markdown.
Be precise and factual — do not invent attributes you cannot observe or infer."""


# ---------------------------------------------------------------------------
# Title Generation
# ---------------------------------------------------------------------------

def build_title_prompt(
    product_name: str,
    brand: str | None = None,
    category: str | None = None,
    attributes: dict | None = None,
    marketplace: str = "amazon",
    tone: str = "professional",
    seller_context: str | None = None,
) -> str:
    attrs_text = ""
    if attributes:
        attrs_text = "\n".join(f"- {k}: {v}" for k, v in attributes.items() if v)

    context_section = ""
    if seller_context:
        context_section = f"\n\nSeller preferences & brand voice:\n{seller_context}"

    limits = {
        "amazon": "Maximum 200 characters. Format: Brand + Key Feature + Product Type + Size/Quantity + Color/Variant",
        "flipkart": "Maximum 150 characters. Format: Brand + Product Type + Key Feature + Color/Size",
        "meesho": "Maximum 100 characters. Short, catchy, mobile-friendly.",
    }

    return f"""Generate an SEO-optimized product title for the following product.

Product Name: {product_name}
Brand: {brand or 'Not specified'}
Category: {category or 'Not specified'}
Marketplace: {marketplace.upper()}
Tone: {tone}
{f'Product Attributes:{chr(10)}{attrs_text}' if attrs_text else ''}
{context_section}

Title rules for {marketplace.upper()}:
{limits.get(marketplace, limits['amazon'])}

Return JSON:
{{
  "title": "The primary optimized title",
  "alternatives": ["2-3 alternative title options"],
  "seo_score": 0-100,
  "keywords_used": ["list of keywords included"]
}}"""


# ---------------------------------------------------------------------------
# Bullet Points / Feature Description
# ---------------------------------------------------------------------------

def build_bullets_prompt(
    product_name: str,
    brand: str | None = None,
    description: str | None = None,
    attributes: dict | None = None,
    marketplace: str = "amazon",
    tone: str = "professional",
    seller_context: str | None = None,
) -> str:
    attrs_text = ""
    if attributes:
        attrs_text = "\n".join(f"- {k}: {v}" for k, v in attributes.items() if v)

    context_section = ""
    if seller_context:
        context_section = f"\n\nSeller preferences & brand voice:\n{seller_context}"

    rules = {
        "amazon": "Exactly 5 bullet points. Each bullet: 150-250 characters. Start with a CAPITAL benefit keyword. Use emojis sparingly.",
        "flipkart": "4-6 bullet points. Each 100-200 characters. Focus on specifications and benefits.",
        "meesho": "3-5 short bullet points. Each under 100 characters. Simple language.",
    }

    return f"""Generate compelling product bullet points for the listing.

Product: {product_name}
Brand: {brand or 'Not specified'}
Description: {description or 'Not provided'}
Marketplace: {marketplace.upper()}
Tone: {tone}
{f'Attributes:{chr(10)}{attrs_text}' if attrs_text else ''}
{context_section}

Rules for {marketplace.upper()}:
{rules.get(marketplace, rules['amazon'])}

Return JSON:
{{
  "bullet_points": ["bullet 1", "bullet 2", ...],
  "quality_score": 0-100
}}"""


# ---------------------------------------------------------------------------
# Product Description
# ---------------------------------------------------------------------------

def build_description_prompt(
    product_name: str,
    brand: str | None = None,
    bullet_points: list[str] | None = None,
    attributes: dict | None = None,
    marketplace: str = "amazon",
    tone: str = "professional",
    seller_context: str | None = None,
) -> str:
    bullets_text = ""
    if bullet_points:
        bullets_text = "\n".join(f"- {b}" for b in bullet_points)

    attrs_text = ""
    if attributes:
        attrs_text = "\n".join(f"- {k}: {v}" for k, v in attributes.items() if v)

    context_section = ""
    if seller_context:
        context_section = f"\n\nSeller preferences & brand voice:\n{seller_context}"

    return f"""Write a compelling product description for the e-commerce listing.

Product: {product_name}
Brand: {brand or 'Not specified'}
Marketplace: {marketplace.upper()}
Tone: {tone}
{f'Key Features:{chr(10)}{bullets_text}' if bullets_text else ''}
{f'Attributes:{chr(10)}{attrs_text}' if attrs_text else ''}
{context_section}

Rules:
- 150-300 words for Amazon, 100-200 for Flipkart/Meesho
- Highlight benefits over features
- Include a call-to-action
- Naturally weave in search keywords

Return JSON:
{{
  "description": "The product description text",
  "word_count": number
}}"""


# ---------------------------------------------------------------------------
# Search Terms & Backend Keywords
# ---------------------------------------------------------------------------

def build_search_terms_prompt(
    product_name: str,
    brand: str | None = None,
    category: str | None = None,
    attributes: dict | None = None,
    marketplace: str = "amazon",
) -> str:
    attrs_text = ""
    if attributes:
        attrs_text = "\n".join(f"- {k}: {v}" for k, v in attributes.items() if v)

    return f"""Generate search terms and backend keywords for this product listing.

Product: {product_name}
Brand: {brand or 'Not specified'}
Category: {category or 'Not specified'}
Marketplace: {marketplace.upper()}
{f'Attributes:{chr(10)}{attrs_text}' if attrs_text else ''}

Rules:
- Amazon: Up to 250 bytes of backend search terms. No brand name, no ASINs, no commas.
- Flipkart: Focus on 10-15 high-volume search keywords.
- Meesho: 5-10 simple, commonly-searched terms.
- Include synonyms, alternate spellings, and related terms.
- Include Hindi/regional equivalents where relevant for Indian marketplaces.

Return JSON:
{{
  "search_terms": ["term1", "term2", ...],
  "backend_keywords": "space-separated string of backend keywords",
  "long_tail_keywords": ["long tail phrase 1", "long tail phrase 2", ...]
}}"""


# ---------------------------------------------------------------------------
# Attribute Extraction / Product DNA
# ---------------------------------------------------------------------------

def build_attribute_extraction_prompt(
    product_name: str,
    description: str | None = None,
    category: str | None = None,
) -> str:
    return f"""Analyze this product and extract structured attributes.

Product: {product_name}
Category: {category or 'Not specified'}
Description: {description or 'Not provided'}

Extract and return JSON:
{{
  "brand": "detected brand or null",
  "material": "primary material",
  "color": "primary color",
  "size": "size if applicable",
  "weight": "weight with unit",
  "dimensions": {{"length": "", "width": "", "height": "", "unit": "cm"}},
  "detected_product_type": "specific product type",
  "key_features": ["feature1", "feature2", ...],
  "target_audience": "who this product is for",
  "use_cases": ["use case 1", "use case 2", ...],
  "country_of_origin": "detected or null"
}}"""


# ---------------------------------------------------------------------------
# Product DNA from Image Analysis
# ---------------------------------------------------------------------------

def build_image_analysis_prompt() -> str:
    return """Analyze this product image and extract the Product DNA.

Return a JSON object with these exact fields:
{
  "shapes": ["list of geometric shapes observed"],
  "dominant_colors": ["hex color codes of dominant colors"],
  "material_appearance": "description of material/texture",
  "detected_product_type": "specific product category",
  "visible_components": ["list of visible parts/components"],
  "approximate_dimensions": {"height": "", "width": "", "depth": "", "unit": "cm"},
  "packaging_characteristics": ["observed packaging details"],
  "visual_features": ["notable visual features like finish, texture, etc."],
  "brand_visible": "brand name if visible on product, else null",
  "text_on_product": ["any text visible on the product"]
}"""


# ---------------------------------------------------------------------------
# Full Listing Generation (all-in-one)
# ---------------------------------------------------------------------------

def build_full_listing_prompt(
    product_name: str,
    brand: str | None = None,
    category: str | None = None,
    description: str | None = None,
    attributes: dict | None = None,
    marketplace: str = "amazon",
    tone: str = "professional",
    seller_context: str | None = None,
) -> str:
    attrs_text = ""
    if attributes:
        attrs_text = "\n".join(f"- {k}: {v}" for k, v in attributes.items() if v)

    context_section = ""
    if seller_context:
        context_section = f"\n\nSeller preferences & brand voice:\n{seller_context}"

    return f"""Generate a complete {marketplace.upper()} product listing for this product.

Product: {product_name}
Brand: {brand or 'Not specified'}
Category: {category or 'Not specified'}
Existing Description: {description or 'Not provided'}
Marketplace: {marketplace.upper()}
Tone: {tone}
{f'Attributes:{chr(10)}{attrs_text}' if attrs_text else ''}
{context_section}

Generate ALL of the following in a single JSON response:
{{
  "title": "SEO-optimized product title",
  "bullet_points": ["5 compelling bullet points"],
  "description": "Detailed product description (150-300 words)",
  "search_terms": ["10-15 search keywords"],
  "backend_keywords": "space-separated backend keywords (max 250 bytes)",
  "predicted_category": "suggested marketplace category path",
  "attributes": {{
    "brand": "",
    "material": "",
    "color": "",
    "size": ""
  }},
  "seo_score": 0-100,
  "quality_score": 0-100
}}"""
