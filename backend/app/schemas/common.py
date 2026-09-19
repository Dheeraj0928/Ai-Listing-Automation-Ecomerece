"""Common schemas used across the application."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: bool = True
    message: str
    details: dict = {}


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    message: str
    data: dict | None = None


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at fields."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
