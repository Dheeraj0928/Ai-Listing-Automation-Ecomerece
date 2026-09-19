"""Validation rule model for marketplace-specific field validation."""

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ValidationRule(Base):
    __tablename__ = "validation_rules"

    marketplace: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # required, max_length, min_length, regex, enum, range
    rule_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="error", nullable=False)  # error, warning, info
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<ValidationRule {self.marketplace}/{self.field_name}: {self.rule_type}>"
