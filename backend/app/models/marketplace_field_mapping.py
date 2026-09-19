"""Marketplace field mapping model."""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MarketplaceFieldMapping(Base):
    __tablename__ = "marketplace_field_mappings"

    marketplace: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    internal_field: Mapped[str] = mapped_column(String(255), nullable=False)
    marketplace_field: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validation_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    enum_values: Mapped[list | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<FieldMapping {self.marketplace}: {self.internal_field} -> {self.marketplace_field}>"
