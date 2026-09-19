"""Audit log repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)

    async def log_action(
        self,
        user_id: uuid.UUID,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        return await self.create(
            {
                "user_id": user_id,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "old_value": old_value,
                "new_value": new_value,
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )

    async def get_recent_activity(
        self, user_id: uuid.UUID, limit: int = 20
    ) -> list[AuditLog]:
        """Get recent audit logs for a user."""
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
