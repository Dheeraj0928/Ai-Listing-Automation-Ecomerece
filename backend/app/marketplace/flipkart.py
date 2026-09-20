"""Real Flipkart Seller API adapter using OAuth2 and Seller API v3."""

from __future__ import annotations

import base64
import uuid
import httpx

from app.marketplace import (
    MarketplaceProvider,
    PublishResult,
    ValidationIssue,
    ValidationResult,
)


class FlipkartAdapter(MarketplaceProvider):
    """Flipkart Seller API adapter."""

    def __init__(self, app_id: str | None = None, app_secret: str | None = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://api.flipkart.net"

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

    async def get_access_token(self) -> tuple[str | None, str | None]:
        """Fetch OAuth2 Bearer token from Flipkart."""
        if not self.app_id or not self.app_secret:
            return None, "Missing Flipkart App ID or App Secret"

        token_url = f"{self.base_url}/oauth-service/oauth/token?grant_type=client_credentials&scope=Seller_Api"
        auth_bytes = f"{self.app_id}:{self.app_secret}".encode("utf-8")
        auth_header = f"Basic {base64.b64encode(auth_bytes).decode('utf-8')}"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(
                    token_url,
                    headers={
                        "Authorization": auth_header,
                        "Accept": "application/json",
                    },
                )
                data = res.json()
                if res.status_code == 200 and "access_token" in data:
                    return data["access_token"], None
                
                err_desc = data.get("error_description") or data.get("error") or res.text
                return None, f"Flipkart Auth Failed: {err_desc}"
        except Exception as exc:
            return None, f"Connection to Flipkart failed: {str(exc)}"

    async def publish_listing(self, listing_data: dict) -> PublishResult:
        """Publish product to Flipkart Seller API."""
        if not self.app_id or not self.app_secret:
            return PublishResult(
                success=False,
                error="Flipkart App ID or App Secret is not configured.",
                message="Please configure Flipkart Developer credentials in Marketplaces.",
            )

        token, err = await self.get_access_token()
        if not token:
            return PublishResult(
                success=False,
                error=err,
                message=f"Could not authenticate with Flipkart: {err}",
            )

        sku = listing_data.get("sku") or f"SKU-{uuid.uuid4().hex[:8].upper()}"
        price = float(listing_data.get("price") or 299)
        mrp = float(listing_data.get("mrp") or price * 1.5)

        payload = {
            sku: {
                "product_id": listing_data.get("fsn") or listing_data.get("product_id") or sku,
                "price": {
                    "mrp": mrp,
                    "selling_price": price,
                    "currency": "INR",
                },
                "listing_status": "ACTIVE",
                "shipping_fees": {},
            }
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    f"{self.base_url}/sellers/v3/listings",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if resp.status_code in [200, 201, 202]:
                    return PublishResult(
                        success=True,
                        marketplace_listing_id=sku,
                        message=f"Successfully sent listing {sku} to Flipkart API.",
                    )
                else:
                    return PublishResult(
                        success=False,
                        error=f"Flipkart API returned {resp.status_code}: {resp.text[:300]}",
                        message="Flipkart rejected the listing payload.",
                    )
        except Exception as e:
            return PublishResult(
                success=False,
                error=str(e),
                message=f"Failed to communicate with Flipkart API: {str(e)}",
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
