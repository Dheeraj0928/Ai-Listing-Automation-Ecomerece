"""Marketplace provider abstract base and mock adapters."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ValidationIssue:
    """A single validation error or warning."""
    field: str
    message: str
    severity: str = "error"  # error | warning | info


@dataclass
class ValidationResult:
    """Result of listing validation against marketplace rules."""
    is_valid: bool
    completion_percentage: float = 0.0
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)


@dataclass
class PublishResult:
    """Result of a publish operation."""
    success: bool
    marketplace_listing_id: str | None = None
    message: str = ""
    error: str | None = None


class MarketplaceProvider(ABC):
    """Abstract base class for marketplace adapters."""

    @property
    @abstractmethod
    def marketplace_name(self) -> str:
        ...

    @abstractmethod
    async def validate_listing(self, listing_data: dict) -> ValidationResult:
        """Validate listing data against marketplace-specific rules."""
        ...

    @abstractmethod
    async def publish_listing(self, listing_data: dict) -> PublishResult:
        """Publish a listing to the marketplace."""
        ...

    @abstractmethod
    async def get_required_fields(self) -> list[dict]:
        """Get the list of required fields for this marketplace."""
        ...


# -------------------------
# Mock adapters for dev
# -------------------------

class MockAmazonAdapter(MarketplaceProvider):
    """Mock Amazon SP-API adapter for development."""

    @property
    def marketplace_name(self) -> str:
        return "amazon"

    async def validate_listing(self, listing_data: dict) -> ValidationResult:
        errors = []
        warnings = []
        data = listing_data or {}
        total_fields = 10
        filled = 0

        # Required Amazon fields
        for required in ["title", "brand", "bullet_points", "description", "price"]:
            if data.get(required):
                filled += 1
            else:
                errors.append(ValidationIssue(field=required, message=f"{required} is required for Amazon"))

        for optional in ["search_terms", "material", "color", "size", "weight"]:
            if data.get(optional):
                filled += 1
            else:
                warnings.append(ValidationIssue(field=optional, message=f"{optional} recommended for better ranking", severity="warning"))

        # Title length check
        title = data.get("title", "")
        if len(title) > 200:
            errors.append(ValidationIssue(field="title", message="Amazon title must be under 200 characters"))

        pct = (filled / total_fields) * 100 if total_fields > 0 else 0
        return ValidationResult(
            is_valid=len(errors) == 0,
            completion_percentage=round(pct, 1),
            errors=errors,
            warnings=warnings,
        )

    async def publish_listing(self, listing_data: dict) -> PublishResult:
        mock_id = f"ASIN-{uuid.uuid4().hex[:10].upper()}"
        return PublishResult(
            success=True,
            marketplace_listing_id=mock_id,
            message=f"Successfully published to Amazon (mock). ASIN: {mock_id}",
        )

    async def get_required_fields(self) -> list[dict]:
        return [
            {"name": "title", "type": "string", "max_length": 200, "required": True},
            {"name": "brand", "type": "string", "max_length": 50, "required": True},
            {"name": "bullet_points", "type": "array", "max_items": 5, "required": True},
            {"name": "description", "type": "text", "max_length": 2000, "required": True},
            {"name": "price", "type": "number", "required": True},
            {"name": "search_terms", "type": "string", "max_length": 250, "required": False},
            {"name": "color", "type": "string", "required": False},
            {"name": "size", "type": "string", "required": False},
            {"name": "material", "type": "string", "required": False},
            {"name": "weight", "type": "number", "required": False},
        ]


class MockFlipkartAdapter(MarketplaceProvider):
    """Mock Flipkart API adapter for development."""

    @property
    def marketplace_name(self) -> str:
        return "flipkart"

    async def validate_listing(self, listing_data: dict) -> ValidationResult:
        errors = []
        warnings = []
        data = listing_data or {}
        total_fields = 8
        filled = 0

        for required in ["title", "description", "price", "brand"]:
            if data.get(required):
                filled += 1
            else:
                errors.append(ValidationIssue(field=required, message=f"{required} is required for Flipkart"))

        for optional in ["key_features", "color", "size", "material"]:
            if data.get(optional):
                filled += 1
            else:
                warnings.append(ValidationIssue(field=optional, message=f"{optional} recommended", severity="warning"))

        pct = (filled / total_fields) * 100 if total_fields > 0 else 0
        return ValidationResult(
            is_valid=len(errors) == 0,
            completion_percentage=round(pct, 1),
            errors=errors,
            warnings=warnings,
        )

    async def publish_listing(self, listing_data: dict) -> PublishResult:
        mock_id = f"FK-{uuid.uuid4().hex[:12].upper()}"
        return PublishResult(
            success=True,
            marketplace_listing_id=mock_id,
            message=f"Successfully published to Flipkart (mock). ID: {mock_id}",
        )

    async def get_required_fields(self) -> list[dict]:
        return [
            {"name": "title", "type": "string", "max_length": 150, "required": True},
            {"name": "brand", "type": "string", "required": True},
            {"name": "description", "type": "text", "max_length": 5000, "required": True},
            {"name": "price", "type": "number", "required": True},
            {"name": "key_features", "type": "array", "max_items": 10, "required": False},
            {"name": "color", "type": "string", "required": False},
            {"name": "size", "type": "string", "required": False},
            {"name": "material", "type": "string", "required": False},
        ]


class MockMeeshoAdapter(MarketplaceProvider):
    """Mock Meesho API adapter for development."""

    @property
    def marketplace_name(self) -> str:
        return "meesho"

    async def validate_listing(self, listing_data: dict) -> ValidationResult:
        errors = []
        warnings = []
        data = listing_data or {}
        total_fields = 6
        filled = 0

        for required in ["title", "description", "price"]:
            if data.get(required):
                filled += 1
            else:
                errors.append(ValidationIssue(field=required, message=f"{required} is required for Meesho"))

        for optional in ["color", "size", "material"]:
            if data.get(optional):
                filled += 1
            else:
                warnings.append(ValidationIssue(field=optional, message=f"{optional} recommended", severity="warning"))

        pct = (filled / total_fields) * 100 if total_fields > 0 else 0
        return ValidationResult(
            is_valid=len(errors) == 0,
            completion_percentage=round(pct, 1),
            errors=errors,
            warnings=warnings,
        )

    async def publish_listing(self, listing_data: dict) -> PublishResult:
        mock_id = f"MEESHO-{uuid.uuid4().hex[:8].upper()}"
        return PublishResult(
            success=True,
            marketplace_listing_id=mock_id,
            message=f"Successfully published to Meesho (mock). ID: {mock_id}",
        )

    async def get_required_fields(self) -> list[dict]:
        return [
            {"name": "title", "type": "string", "max_length": 100, "required": True},
            {"name": "description", "type": "text", "max_length": 3000, "required": True},
            {"name": "price", "type": "number", "required": True},
            {"name": "color", "type": "string", "required": False},
            {"name": "size", "type": "string", "required": False},
            {"name": "material", "type": "string", "required": False},
        ]


def get_marketplace_adapter(marketplace: str) -> MarketplaceProvider:
    """Factory to get the right marketplace adapter."""
    adapters: dict[str, type[MarketplaceProvider]] = {
        "amazon": MockAmazonAdapter,
        "flipkart": MockFlipkartAdapter,
        "meesho": MockMeeshoAdapter,
    }
    adapter_cls = adapters.get(marketplace.lower())
    if not adapter_cls:
        raise ValueError(f"Unknown marketplace: {marketplace}. Supported: {list(adapters.keys())}")
    return adapter_cls()
