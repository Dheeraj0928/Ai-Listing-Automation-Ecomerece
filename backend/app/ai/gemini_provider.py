"""Google Gemini provider implementation using the new google.genai SDK."""

import json
import logging

from google import genai
from google.genai import types

from app.ai.base import AIGenerationResult, AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """AI provider backed by Google Gemini API (new google.genai SDK)."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        self._client = genai.Client(api_key=settings.GOOGLE_AI_API_KEY)
        self._model_name = model

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: str = "text",
    ) -> AIGenerationResult:
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        if system_prompt:
            config.system_instruction = system_prompt

        response = await self._client.aio.models.generate_content(
            model=self._model_name,
            contents=prompt,
            config=config,
        )

        text = response.text or ""
        token_count = self._count_tokens(response)

        return AIGenerationResult(
            content=text,
            provider=self.provider_name,
            model=self._model_name,
            tokens_used=token_count,
            cost_estimate=self._estimate_cost(token_count),
            confidence_score=0.85,
            raw_response={"text": text},
        )

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AIGenerationResult:
        sys_content = (system_prompt or "") + "\nYou MUST respond with valid JSON only. No markdown, no code fences, no explanation."

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
            system_instruction=sys_content.strip(),
        )

        response = await self._client.aio.models.generate_content(
            model=self._model_name,
            contents=prompt,
            config=config,
        )

        raw_text = response.text or "{}"
        token_count = self._count_tokens(response)

        # Clean potential markdown code fences
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Gemini returned invalid JSON, wrapping as raw string")
            parsed = {"raw": raw_text}

        return AIGenerationResult(
            content=parsed,
            provider=self.provider_name,
            model=self._model_name,
            tokens_used=token_count,
            cost_estimate=self._estimate_cost(token_count),
            confidence_score=0.87,
            raw_response={"text": raw_text},
        )

    async def analyze_image(
        self,
        image_url_or_base64: str,
        prompt: str,
        max_tokens: int = 4096,
    ) -> AIGenerationResult:
        import base64

        # Build the image part for Gemini
        if image_url_or_base64.startswith(("http://", "https://")):
            # Download the image first
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(image_url_or_base64)
                image_bytes = resp.content
                mime_type = resp.headers.get("content-type", "image/jpeg")
        else:
            image_bytes = base64.b64decode(image_url_or_base64)
            mime_type = "image/jpeg"

        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        config = types.GenerateContentConfig(
            max_output_tokens=max_tokens,
        )

        response = await self._client.aio.models.generate_content(
            model=self._model_name,
            contents=[prompt, image_part],
            config=config,
        )

        raw_text = response.text or ""
        token_count = self._count_tokens(response)

        try:
            parsed = json.loads(raw_text)
            content = parsed
        except json.JSONDecodeError:
            content = raw_text

        return AIGenerationResult(
            content=content,
            provider=self.provider_name,
            model=self._model_name,
            tokens_used=token_count,
            cost_estimate=self._estimate_cost(token_count),
            confidence_score=0.85,
            raw_response={"text": raw_text},
        )

    def _count_tokens(self, response) -> int:
        """Extract token usage from Gemini response."""
        try:
            usage = response.usage_metadata
            return (usage.prompt_token_count or 0) + (usage.candidates_token_count or 0)
        except Exception:
            return 0

    def _estimate_cost(self, total_tokens: int) -> float:
        """Rough cost estimate for Gemini models."""
        cost_per_1k = {
            "gemini-2.0-flash": 0.0001,
            "gemini-1.5-flash": 0.000075,
            "gemini-1.5-pro": 0.00125,
        }
        rate = cost_per_1k.get(self._model_name, 0.0001)
        return round((total_tokens / 1000) * rate, 6)
