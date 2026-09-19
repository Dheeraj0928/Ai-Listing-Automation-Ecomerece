"""Category model for internal and marketplace-specific categories."""

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True
    )
    marketplace: Mapped[str] = mapped_column(String(50), default="internal", nullable=False)
    marketplace_category_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    required_attributes: Mapped[list | None] = mapped_column(JSON, nullable=True)
    optional_attributes: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Category {self.name} ({self.marketplace})>"
