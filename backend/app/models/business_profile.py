"""Business profile model."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    business_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacturer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacturer_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    manufacturer_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacturer_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacturer_pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    country_of_origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    importer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    importer_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    packer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    packer_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    gstin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    business_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    warehouse_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    return_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON config: which fields to auto-fill, marketplace-specific, product-specific
    auto_fill_config: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)

    # Relationships
    user = relationship("User", back_populates="business_profile")

    def __repr__(self) -> str:
        return f"<BusinessProfile {self.business_name}>"
