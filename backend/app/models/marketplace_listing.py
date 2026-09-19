"""Marketplace listing model."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    marketplace: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    marketplace_listing_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status: draft, ai_generated, validated, needs_review, approved, publishing, published, error
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False, index=True)

    listing_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    marketplace_specific_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    completion_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    validation_results: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="listings")
    versions = relationship("ListingVersion", back_populates="listing", order_by="ListingVersion.version_number")

    def __repr__(self) -> str:
        return f"<MarketplaceListing {self.marketplace} ({self.status})>"
