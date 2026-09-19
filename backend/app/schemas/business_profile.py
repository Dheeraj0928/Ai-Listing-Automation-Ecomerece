"""Business profile schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class BusinessProfileRequest(BaseModel):
    """Request body for creating/updating business profile."""
    business_name: str | None = Field(None, max_length=255)
    manufacturer_name: str | None = Field(None, max_length=255)
    manufacturer_address: str | None = None
    manufacturer_city: str | None = Field(None, max_length=100)
    manufacturer_state: str | None = Field(None, max_length=100)
    manufacturer_pincode: str | None = Field(None, max_length=10)
    country_of_origin: str | None = Field(None, max_length=100)
    importer_name: str | None = Field(None, max_length=255)
    importer_address: str | None = None
    packer_name: str | None = Field(None, max_length=255)
    packer_address: str | None = None
    gstin: str | None = Field(None, max_length=20)
    business_email: EmailStr | None = None
    business_phone: str | None = Field(None, max_length=20)
    warehouse_address: str | None = None
    return_address: str | None = None


class AutoFillConfigRequest(BaseModel):
    """Request body for updating auto-fill configuration."""
    auto_fill_config: dict
    # Example: {"manufacturer_name": {"auto_fill": true, "scope": "global"},
    #           "manufacturer_address": {"auto_fill": true, "scope": "marketplace", "marketplace": "amazon"}}


class BusinessProfileResponse(BaseModel):
    """Business profile response."""
    id: UUID
    user_id: UUID
    business_name: str | None = None
    manufacturer_name: str | None = None
    manufacturer_address: str | None = None
    manufacturer_city: str | None = None
    manufacturer_state: str | None = None
    manufacturer_pincode: str | None = None
    country_of_origin: str | None = None
    importer_name: str | None = None
    importer_address: str | None = None
    packer_name: str | None = None
    packer_address: str | None = None
    gstin: str | None = None
    business_email: str | None = None
    business_phone: str | None = None
    warehouse_address: str | None = None
    return_address: str | None = None
    auto_fill_config: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
