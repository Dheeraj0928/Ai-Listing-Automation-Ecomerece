"""OpenAI provider implementation (GPT-4o / GPT-4o-mini)."""

import json
import logging

from openai import AsyncOpenAI

from app.ai.base import AIGenerationResult, AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """AI provider backed by the OpenAI API."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = model

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: str = "text",
    ) -> AIGenerationResult:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        choice = response.choices[0]
        usage = response.usage

        return AIGenerationResult(
            content=choice.message.content or "",
            provider=self.provider_name,
            model=self._model,
            tokens_used=usage.total_tokens if usage else 0,
            cost_estimate=self._estimate_cost(usage.total_tokens if usage else 0),
            confidence_score=0.85,
            raw_response=response.model_dump(),
        )

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AIGenerationResult:
        messages = []
        sys_content = (system_prompt or "") + "\nYou MUST respond with valid JSON only. No markdown, no code fences."
        messages.append({"role": "system", "content": sys_content.strip()})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        choice = response.choices[0]
        usage = response.usage
        raw_text = choice.message.content or "{}"

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.warning("OpenAI returned invalid JSON, wrapping as raw string")
            parsed = {"raw": raw_text}

        return AIGenerationResult(
            content=parsed,
            provider=self.provider_name,
            model=self._model,
            tokens_used=usage.total_tokens if usage else 0,
            cost_estimate=self._estimate_cost(usage.total_tokens if usage else 0),
            confidence_score=0.9,
            raw_response=response.model_dump(),
        )

    async def analyze_image(
        self,
        image_url_or_base64: str,
        prompt: str,
        max_tokens: int = 4096,
    ) -> AIGenerationResult:
        # Detect if the input is a URL or base64
        if image_url_or_base64.startswith(("http://", "https://")):
            image_content = {"type": "image_url", "image_url": {"url": image_url_or_base64}}
        else:
            image_content = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_url_or_base64}"},
            }

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    image_content,
                ],
            }
        ]

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
        )

        choice = response.choices[0]
        usage = response.usage
        raw_text = choice.message.content or ""

        # Try to parse as JSON
        try:
            parsed = json.loads(raw_text)
            content = parsed
        except json.JSONDecodeError:
            content = raw_text

        return AIGenerationResult(
            content=content,
            provider=self.provider_name,
            model=self._model,
            tokens_used=usage.total_tokens if usage else 0,
            cost_estimate=self._estimate_cost(usage.total_tokens if usage else 0),
            confidence_score=0.85,
            raw_response=response.model_dump(),
        )

    def _estimate_cost(self, total_tokens: int) -> float:
        """Rough cost estimate based on model pricing."""
        cost_per_1k = {
            "gpt-4o": 0.005,
            "gpt-4o-mini": 0.00015,
            "gpt-4-turbo": 0.01,
        }
        rate = cost_per_1k.get(self._model, 0.001)
        return round((total_tokens / 1000) * rate, 6)
