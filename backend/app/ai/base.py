"""Abstract base class for AI providers — defines the contract every provider must implement."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AIGenerationResult:
    """Standard result object returned by every AI provider."""

    content: str | dict
    provider: str
    model: str
    tokens_used: int = 0
    cost_estimate: float = 0.0
    confidence_score: float = 0.0
    raw_response: dict = field(default_factory=dict)


class AIProvider(ABC):
    """Abstract AI provider — one implementation per supported LLM family."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier (e.g. 'openai', 'gemini')."""
        ...

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: str = "text",
    ) -> AIGenerationResult:
        """Generate text content from a prompt."""
        ...

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AIGenerationResult:
        """Generate structured JSON content from a prompt."""
        ...

    @abstractmethod
    async def analyze_image(
        self,
        image_url_or_base64: str,
        prompt: str,
        max_tokens: int = 4096,
    ) -> AIGenerationResult:
        """Analyze an image and return structured observations."""
        ...
