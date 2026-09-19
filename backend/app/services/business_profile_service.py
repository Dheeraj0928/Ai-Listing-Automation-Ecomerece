"""Business profile service."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.business_profile_repo import BusinessProfileRepository
from app.schemas.business_profile import (
    AutoFillConfigRequest,
    BusinessProfileRequest,
    BusinessProfileResponse,
)


class BusinessProfileService:
    """Business profile management logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_repo = BusinessProfileRepository(db)
        self.audit_repo = AuditRepository(db)

    async def get_profile(self, user: User) -> BusinessProfileResponse | None:
        """Get the business profile for the current user."""
        profile = await self.profile_repo.get_by_user_id(user.id)
        if profile is None:
            return None
        return BusinessProfileResponse.model_validate(profile)

    async def upsert_profile(
        self, user: User, data: BusinessProfileRequest
    ) -> BusinessProfileResponse:
        """Create or update the business profile."""
        profile_data = data.model_dump(exclude_unset=True)
        profile = await self.profile_repo.upsert(user.id, profile_data)

        await self.audit_repo.log_action(
            user_id=user.id,
            action="business_profile_updated",
            entity_type="business_profile",
            entity_id=profile.id,
            new_value=profile_data,
        )

        return BusinessProfileResponse.model_validate(profile)

    async def update_auto_fill_config(
        self, user: User, data: AutoFillConfigRequest
    ) -> BusinessProfileResponse:
        """Update the auto-fill configuration."""
        profile = await self.profile_repo.get_by_user_id(user.id)

        if profile is None:
            # Create profile with just the auto-fill config
            profile = await self.profile_repo.create(
                {"user_id": user.id, "auto_fill_config": data.auto_fill_config}
            )
        else:
            # Merge with existing config
            existing_config = profile.auto_fill_config or {}
            existing_config.update(data.auto_fill_config)
            profile.auto_fill_config = existing_config
            await self.db.flush()
            await self.db.refresh(profile)

        await self.audit_repo.log_action(
            user_id=user.id,
            action="auto_fill_config_updated",
            entity_type="business_profile",
            entity_id=profile.id,
            new_value={"auto_fill_config": data.auto_fill_config},
        )

        return BusinessProfileResponse.model_validate(profile)
