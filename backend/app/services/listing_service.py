"""Listing service — CRUD, versioning, and status management for marketplace listings."""

import math
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError, ValidationError
from app.models.listing_version import ListingVersion
from app.models.marketplace_listing import MarketplaceListing
from app.models.product import Product
from app.models.publish_job import PublishJob
from app.repositories.audit_repo import AuditRepository
from app.repositories.listing_repo import ListingRepository
from app.repositories.marketplace_repo import MarketplaceRepository
from app.schemas.listing import (
    ListingListResponse,
    ListingResponse,
    ListingUpdateRequest,
    ListingVersionResponse,
)


class ListingService:
    """Marketplace listing business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.listing_repo = ListingRepository(db)
        self.marketplace_repo = MarketplaceRepository(db)
        self.audit_repo = AuditRepository(db)

    async def get_listing(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> ListingResponse:
        """Get a single listing by ID."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if listing is None or listing.user_id != user_id:
            raise NotFoundError("Listing", str(listing_id))
        return ListingResponse.model_validate(listing)

    async def list_listings(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        marketplace: str | None = None,
        status: str | None = None,
        product_id: uuid.UUID | None = None,
    ) -> ListingListResponse:
        """List listings with pagination and filters."""
        offset = (page - 1) * page_size
        filters = [
            MarketplaceListing.user_id == user_id,
            MarketplaceListing.deleted_at.is_(None),
        ]
        if marketplace:
            filters.append(MarketplaceListing.marketplace == marketplace)
        if status:
            filters.append(MarketplaceListing.status == status)
        if product_id:
            filters.append(MarketplaceListing.product_id == product_id)

        items = await self.listing_repo.get_all(offset=offset, limit=page_size, filters=filters)
        total = await self.listing_repo.count(filters=filters)

        return ListingListResponse(
            items=[ListingResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        )

    async def update_listing(
        self, user_id: uuid.UUID, listing_id: uuid.UUID, data: ListingUpdateRequest
    ) -> ListingResponse:
        """Update listing data and create a version snapshot."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if listing is None or listing.user_id != user_id:
            raise NotFoundError("Listing", str(listing_id))

        # Save current state as version
        await self._create_version_snapshot(listing, changed_by="user", change_reason="Manual edit")

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(listing, key, value)
        listing.version += 1

        await self.db.flush()
        await self.db.refresh(listing)

        await self.audit_repo.log_action(
            user_id=user_id,
            action="listing_updated",
            entity_type="listing",
            entity_id=listing.id,
            new_value={"marketplace": listing.marketplace, "status": listing.status},
        )

        return ListingResponse.model_validate(listing)

    async def approve_listing(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> ListingResponse:
        """Mark a listing as approved for publishing."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if listing is None or listing.user_id != user_id:
            raise NotFoundError("Listing", str(listing_id))

        listing.status = "approved"
        await self.db.flush()
        await self.db.refresh(listing)

        await self.audit_repo.log_action(
            user_id=user_id,
            action="listing_approved",
            entity_type="listing",
            entity_id=listing.id,
        )
        return ListingResponse.model_validate(listing)

    async def publish_listing(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> dict:
        """Publish a listing to its marketplace (mock)."""
        from app.marketplace import get_marketplace_adapter

        listing = await self.listing_repo.get_by_id(listing_id)
        if listing is None or listing.user_id != user_id:
            raise NotFoundError("Listing", str(listing_id))

        import json
        adapter = None
        if listing.marketplace.lower() == "flipkart":
            account = await self.marketplace_repo.get_by_marketplace(user_id, "flipkart")
            if account and account.encrypted_credentials:
                try:
                    creds = json.loads(account.encrypted_credentials)
                    app_id = creds.get("app_id")
                    app_secret = creds.get("app_secret")
                    if app_id and app_secret:
                        from app.marketplace.flipkart import FlipkartAdapter
                        adapter = FlipkartAdapter(app_id=app_id, app_secret=app_secret)
                except Exception:
                    pass

        if adapter is None:
            adapter = get_marketplace_adapter(listing.marketplace)

        listing.status = "publishing"
        await self.db.flush()

        # Create tracking publish job
        job = PublishJob(
            listing_id=listing.id,
            user_id=user_id,
            marketplace=listing.marketplace,
            status="processing",
            request_payload=listing.listing_data or {},
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(job)
        await self.db.flush()

        try:
            result = await adapter.publish_listing(listing.listing_data or {})
            if result.success:
                listing.status = "published"
                listing.marketplace_listing_id = result.marketplace_listing_id
                listing.published_at = datetime.now(timezone.utc)
                listing.last_synced_at = datetime.now(timezone.utc)
                listing.error_message = None
                job.status = "completed"
                job.response_payload = {
                    "marketplace_listing_id": result.marketplace_listing_id,
                    "message": result.message,
                }
                job.completed_at = datetime.now(timezone.utc)
            else:
                listing.status = "error"
                listing.error_message = result.error or result.message
                job.status = "failed"
                job.error_message = listing.error_message
                job.completed_at = datetime.now(timezone.utc)
        except Exception as e:
            listing.status = "error"
            listing.error_message = str(e)
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(listing)

        await self.audit_repo.log_action(
            user_id=user_id,
            action="listing_published" if listing.status == "published" else "listing_publish_failed",
            entity_type="listing",
            entity_id=listing.id,
            new_value={"status": listing.status, "marketplace": listing.marketplace, "listing_id": listing.marketplace_listing_id},
        )

        return {
            "success": listing.status == "published",
            "listing_id": str(listing.id),
            "marketplace": listing.marketplace,
            "marketplace_listing_id": listing.marketplace_listing_id,
            "published_at": listing.published_at.isoformat() if listing.published_at else None,
            "last_synced_at": listing.last_synced_at.isoformat() if listing.last_synced_at else None,
            "message": f"Listing {'published' if listing.status == 'published' else 'failed'}: {listing.error_message or 'OK'}",
        }

    async def sync_listing_price_and_inventory(
        self, user_id: uuid.UUID, listing_id: uuid.UUID
    ) -> dict:
        """Synchronize the listing's price and stock from master product."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if listing is None or listing.user_id != user_id:
            raise NotFoundError("Listing", str(listing_id))

        product_result = await self.db.execute(
            select(Product).where(Product.id == listing.product_id, Product.user_id == user_id)
        )
        product = product_result.scalar_one_or_none()
        if not product:
            raise NotFoundError("Product", str(listing.product_id))

        # Snapshot before sync
        await self._create_version_snapshot(
            listing, changed_by="system", change_reason="Pre-sync snapshot (price & inventory)"
        )

        updated_data = dict(listing.listing_data or {})
        if product.price is not None:
            updated_data["price"] = float(product.price)
        if product.mrp is not None:
            updated_data["mrp"] = float(product.mrp)
        if product.stock is not None:
            updated_data["stock"] = product.stock

        listing.listing_data = updated_data
        listing.version += 1
        listing.last_synced_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(listing)

        await self._create_version_snapshot(
            listing, changed_by="user", change_reason="Synced price & inventory from master product"
        )

        await self.audit_repo.log_action(
            user_id=user_id,
            action="listing_synced",
            entity_type="listing",
            entity_id=listing.id,
            new_value={"price": float(product.price or 0), "stock": product.stock, "synced_at": listing.last_synced_at.isoformat()},
        )

        return {
            "success": True,
            "listing_id": str(listing.id),
            "marketplace": listing.marketplace,
            "price": float(product.price or 0),
            "stock": product.stock,
            "synced_at": listing.last_synced_at.isoformat(),
            "message": f"Successfully synced price ({product.price}) and inventory ({product.stock}) with {listing.marketplace.title()}",
        }

    async def rollback_version(
        self, user_id: uuid.UUID, listing_id: uuid.UUID, version_id: uuid.UUID
    ) -> ListingResponse:
        """Rollback a listing to a previous version snapshot."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if listing is None or listing.user_id != user_id:
            raise NotFoundError("Listing", str(listing_id))

        ver_result = await self.db.execute(
            select(ListingVersion).where(
                ListingVersion.id == version_id,
                ListingVersion.listing_id == listing_id,
            )
        )
        target_version = ver_result.scalar_one_or_none()
        if not target_version:
            raise NotFoundError("ListingVersion", str(version_id))

        # Snapshot current state before rolling back
        await self._create_version_snapshot(
            listing, changed_by="user", change_reason=f"Pre-rollback snapshot before reverting to v{target_version.version_number}"
        )

        # Restore from snapshot
        snap = target_version.snapshot or {}
        if "listing_data" in snap:
            listing.listing_data = snap["listing_data"]
        if "marketplace_specific_data" in snap:
            listing.marketplace_specific_data = snap["marketplace_specific_data"]

        listing.version += 1

        await self.db.flush()
        await self.db.refresh(listing)

        # Snapshot the restored version
        await self._create_version_snapshot(
            listing, changed_by="user", change_reason=f"Rolled back to v{target_version.version_number}"
        )

        await self.audit_repo.log_action(
            user_id=user_id,
            action="listing_rolled_back",
            entity_type="listing",
            entity_id=listing.id,
            new_value={"restored_from_version": target_version.version_number, "new_version": listing.version},
        )

        return ListingResponse.model_validate(listing)


    async def get_versions(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> list[ListingVersionResponse]:
        """Get version history for a listing."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if listing is None or listing.user_id != user_id:
            raise NotFoundError("Listing", str(listing_id))

        result = await self.db.execute(
            select(ListingVersion)
            .where(ListingVersion.listing_id == listing_id)
            .order_by(ListingVersion.version_number.desc())
        )
        versions = result.scalars().all()
        return [ListingVersionResponse.model_validate(v) for v in versions]

    async def delete_listing(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> bool:
        """Soft-delete a listing."""
        listing = await self.listing_repo.get_by_id(listing_id)
        if listing is None or listing.user_id != user_id:
            raise NotFoundError("Listing", str(listing_id))
        await self.listing_repo.soft_delete(listing_id)
        return True

    # ------ internal helpers ------

    async def _create_version_snapshot(
        self, listing: MarketplaceListing, changed_by: str = "system", change_reason: str = ""
    ) -> ListingVersion:
        """Snapshot the current listing state as a version."""
        version = ListingVersion(
            listing_id=listing.id,
            version_number=listing.version,
            snapshot={
                "listing_data": listing.listing_data,
                "marketplace_specific_data": listing.marketplace_specific_data,
                "status": listing.status,
            },
            changes=None,
            changed_by=changed_by,
            change_reason=change_reason,
        )
        self.db.add(version)
        await self.db.flush()
        return version
