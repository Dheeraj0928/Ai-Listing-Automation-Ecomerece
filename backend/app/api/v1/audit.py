"""Audit log API routes."""

import uuid
import math
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.audit_log import AuditLog
from app.models.user import User

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List audit logs with filtering and pagination."""
    filters = [AuditLog.user_id == user.id]
    if action:
        filters.append(AuditLog.action == action)
    if entity_type:
        filters.append(AuditLog.entity_type == entity_type)

    # Count
    count_q = select(func.count()).select_from(AuditLog).where(*filters)
    total = (await db.execute(count_q)).scalar_one()

    # Fetch
    offset = (page - 1) * page_size
    query = (
        select(AuditLog)
        .where(*filters)
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "items": [
            {
                "id": str(log.id),
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": str(log.entity_id) if log.entity_id else None,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


@router.get("/actions")
async def list_distinct_actions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of distinct audit actions for filter dropdown."""
    result = await db.execute(
        select(AuditLog.action)
        .where(AuditLog.user_id == user.id)
        .distinct()
        .order_by(AuditLog.action)
    )
    return {"actions": [row[0] for row in result.all()]}
