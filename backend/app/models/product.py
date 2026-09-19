"""Product model — the single source of truth for each product."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True
    )
    subcategory: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    short_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    bullet_points: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # Pricing
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    mrp: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    cost_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Inventory
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Attributes
    color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size: Mapped[str | None] = mapped_column(String(100), nullable=True)
    material: Mapped[str | None] = mapped_column(String(255), nullable=True)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    dimensions: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {length, width, height, unit}

    # Source info (can override business profile)
    country_of_origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacturer_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    packer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    importer: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # SEO
    keywords: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    search_terms: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False, index=True)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="products")
    category = relationship("Category", lazy="selectin")
    images = relationship("ProductImage", back_populates="product", lazy="selectin", order_by="ProductImage.sort_order")
    dna = relationship("ProductDNA", back_populates="product", uselist=False, lazy="selectin")
    listings = relationship("MarketplaceListing", back_populates="product", lazy="select")

    def __repr__(self) -> str:
        return f"<Product {self.sku}: {self.product_name}>"
