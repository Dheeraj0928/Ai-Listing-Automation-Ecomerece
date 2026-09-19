"""Listing version model for tracking change history."""

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ListingVersion(Base):
    __tablename__ = "listing_versions"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("marketplace_listings.id", ondelete="CASCADE"), nullable=False, index=True
    )

    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    changes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    changed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    listing = relationship("MarketplaceListing", back_populates="versions")

    def __repr__(self) -> str:
        return f"<ListingVersion v{self.version_number}>"
