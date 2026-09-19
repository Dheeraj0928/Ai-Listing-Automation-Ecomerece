"""Product DNA model — AI-extracted visual characteristics."""

import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from datetime import datetime

from app.core.database import Base


class ProductDNA(Base):
    __tablename__ = "product_dna"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    shapes: Mapped[list | None] = mapped_column(JSON, nullable=True)
    dominant_colors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    material_appearance: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detected_product_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    visible_components: Mapped[list | None] = mapped_column(JSON, nullable=True)
    approximate_dimensions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    packaging_characteristics: Mapped[list | None] = mapped_column(JSON, nullable=True)
    visual_features: Mapped[list | None] = mapped_column(JSON, nullable=True)
    raw_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)

    ai_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="dna")

    def __repr__(self) -> str:
        return f"<ProductDNA product={self.product_id}>"
