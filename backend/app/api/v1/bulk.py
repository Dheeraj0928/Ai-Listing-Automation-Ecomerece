"""Bulk operations API routes — import, export, bulk generate."""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ValidationError
from app.models.user import User
from app.services.bulk_service import BulkService

router = APIRouter(prefix="/bulk", tags=["Bulk Operations"])


class BulkGenerateRequest(BaseModel):
    product_ids: list[uuid.UUID]
    marketplaces: list[str] = ["amazon", "flipkart", "meesho"]
    tone: str = "professional"
    provider: str | None = None


@router.post("/import")
async def bulk_import(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload CSV or Excel file to bulk import products. Returns job_id for progress tracking."""
    if not file.filename:
        raise ValidationError("No file uploaded")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("csv", "xlsx", "xls"):
        raise ValidationError("Supported formats: CSV, XLSX")

    content = await file.read()
    service = BulkService(db)

    if ext == "csv":
        rows = await service.parse_csv(content)
    else:
        rows = await service.parse_excel(content)

    if not rows:
        raise ValidationError("No valid product rows found in the file.")

    job_id = str(uuid.uuid4())

    # Run bulk creation in background
    async def _run():
        await service.bulk_create_products(user.id, rows, job_id)

    background_tasks.add_task(_run)

    return {
        "job_id": job_id,
        "total_rows": len(rows),
        "message": f"Import started. {len(rows)} products queued for creation.",
    }


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the progress of a bulk import or generate job."""
    service = BulkService(db)
    return await service.get_job_status(job_id)


@router.post("/generate")
async def bulk_generate(
    data: BulkGenerateRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk generate AI listings for selected products across marketplaces."""
    if not data.product_ids:
        raise ValidationError("No product IDs provided")

    job_id = str(uuid.uuid4())
    service = BulkService(db)

    async def _run():
        await service.bulk_generate_listings(
            user_id=user.id,
            product_ids=data.product_ids,
            marketplaces=data.marketplaces,
            tone=data.tone,
            provider=data.provider,
            job_id=job_id,
        )

    background_tasks.add_task(_run)

    total = len(data.product_ids) * len(data.marketplaces)
    return {
        "job_id": job_id,
        "total": total,
        "message": f"Bulk generation started for {len(data.product_ids)} products × {len(data.marketplaces)} marketplaces.",
    }


@router.get("/export")
async def export_products(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export all products as CSV download."""
    service = BulkService(db)
    csv_content = await service.export_products_csv(user.id)

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products_export.csv"},
    )


@router.get("/template")
async def download_template(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a blank CSV template for bulk import."""
    service = BulkService(db)
    csv_content = service.generate_template_csv()

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=import_template.csv"},
    )
