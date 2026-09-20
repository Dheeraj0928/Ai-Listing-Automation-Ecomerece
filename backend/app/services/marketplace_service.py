"""Marketplace service — manage marketplace account connections."""

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.audit_repo import AuditRepository
from app.repositories.marketplace_repo import MarketplaceRepository
from app.schemas.marketplace import (
    MarketplaceAccountCreate,
    MarketplaceAccountListResponse,
    MarketplaceAccountResponse,
    MarketplaceAccountUpdate,
)


class MarketplaceService:
    """Marketplace account business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.marketplace_repo = MarketplaceRepository(db)
        self.audit_repo = AuditRepository(db)

    async def connect_marketplace(
        self, user_id: uuid.UUID, data: MarketplaceAccountCreate
    ) -> MarketplaceAccountResponse:
        """Connect a new marketplace account."""
        existing = await self.marketplace_repo.get_by_marketplace(user_id, data.marketplace)
        if existing:
            existing.status = "connected"
            existing.account_name = data.account_name or f"My {data.marketplace.title()} Account"
            if data.account_id:
                existing.account_id = data.account_id
            if data.credentials:
                existing.encrypted_credentials = json.dumps(data.credentials)
            if data.config:
                existing.config = data.config
            existing.last_error = None
            await self.db.flush()
            await self.db.refresh(existing)
            account = existing
        else:
            account_data = {
                "user_id": user_id,
                "marketplace": data.marketplace,
                "account_id": data.account_id,
                "account_name": data.account_name or f"My {data.marketplace.title()} Account",
                "status": "connected",
                "encrypted_credentials": json.dumps(data.credentials) if data.credentials else None,
                "config": data.config,
            }
            account = await self.marketplace_repo.create(account_data)

        await self.audit_repo.log_action(
            user_id=user_id,
            action="marketplace_connected",
            entity_type="marketplace_account",
            entity_id=account.id,
            new_value={"marketplace": data.marketplace},
        )

        return MarketplaceAccountResponse.model_validate(account)

    async def list_accounts(self, user_id: uuid.UUID) -> MarketplaceAccountListResponse:
        """List all marketplace accounts for a user."""
        accounts = await self.marketplace_repo.get_user_accounts(user_id)
        return MarketplaceAccountListResponse(
            items=[MarketplaceAccountResponse.model_validate(a) for a in accounts],
            total=len(accounts),
        )

    async def get_account(
        self, user_id: uuid.UUID, marketplace: str
    ) -> MarketplaceAccountResponse:
        """Get a specific marketplace account."""
        account = await self.marketplace_repo.get_by_marketplace(user_id, marketplace)
        if not account:
            raise NotFoundError("Marketplace account", marketplace)
        return MarketplaceAccountResponse.model_validate(account)

    async def update_account(
        self, user_id: uuid.UUID, marketplace: str, data: MarketplaceAccountUpdate
    ) -> MarketplaceAccountResponse:
        """Update marketplace account configuration."""
        account = await self.marketplace_repo.get_by_marketplace(user_id, marketplace)
        if not account:
            raise NotFoundError("Marketplace account", marketplace)

        update_dict = data.model_dump(exclude_unset=True)
        if "credentials" in update_dict:
            creds = update_dict.pop("credentials")
            update_dict["encrypted_credentials"] = json.dumps(creds) if creds else None

        for key, value in update_dict.items():
            setattr(account, key, value)

        await self.db.flush()
        await self.db.refresh(account)

        return MarketplaceAccountResponse.model_validate(account)

    async def disconnect_marketplace(self, user_id: uuid.UUID, marketplace: str) -> bool:
        """Disconnect a marketplace account."""
        account = await self.marketplace_repo.get_by_marketplace(user_id, marketplace)
        if not account:
            raise NotFoundError("Marketplace account", marketplace)

        account.status = "disconnected"
        account.encrypted_credentials = None
        await self.db.flush()

        await self.audit_repo.log_action(
            user_id=user_id,
            action="marketplace_disconnected",
            entity_type="marketplace_account",
            entity_id=account.id,
            new_value={"marketplace": marketplace},
        )
        return True

    async def sync_marketplace(self, user_id: uuid.UUID, marketplace: str) -> dict:
        """Trigger a sync with the marketplace (mock)."""
        account = await self.marketplace_repo.get_by_marketplace(user_id, marketplace)
        if not account:
            raise NotFoundError("Marketplace account", marketplace)

        # Mock sync — in production this would call the marketplace API
        account.last_sync_at = datetime.now(timezone.utc)
        account.last_error = None
        await self.db.flush()

        return {
            "success": True,
            "marketplace": marketplace,
            "synced_at": account.last_sync_at.isoformat(),
            "message": f"Successfully synced with {marketplace.title()} (mock)",
        }
