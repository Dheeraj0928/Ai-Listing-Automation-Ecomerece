"""Seller memory model — learn once, reuse forever."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SellerMemory(Base):
    __tablename__ = "seller_memory"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    field_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    field_value: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)  # manual, ai_suggested, imported
    scope: Mapped[str] = mapped_column(String(50), default="global", nullable=False)  # global, marketplace, product
    marketplace: Mapped[str | None] = mapped_column(String(50), nullable=True)  # amazon, flipkart, meesho
    product_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="seller_memories")

    def __repr__(self) -> str:
        return f"<SellerMemory {self.field_name}={self.field_value[:30]}>"
