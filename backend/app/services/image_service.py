"""Image management service — upload, delete, reorder, set primary."""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.models.product import Product
from app.models.product_image import ProductImage

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGES_PER_PRODUCT = 8


class ImageService:
    """Product image upload and management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _product_upload_dir(self, product_id: uuid.UUID) -> Path:
        base = Path(settings.UPLOAD_DIR)
        product_dir = base / "products" / str(product_id)
        product_dir.mkdir(parents=True, exist_ok=True)
        return product_dir

    async def _get_product(self, product_id: uuid.UUID, user_id: uuid.UUID) -> Product:
        result = await self.db.execute(
            select(Product).where(Product.id == product_id, Product.user_id == user_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundError("Product", str(product_id))
        return product

    async def _count_images(self, product_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(ProductImage).where(ProductImage.product_id == product_id)
        )
        return len(result.scalars().all())

    async def upload_images(
        self,
        user_id: uuid.UUID,
        product_id: uuid.UUID,
        files: list[UploadFile],
        image_type: str = "main",
    ) -> list[dict]:
        """Upload one or more images to a product."""
        product = await self._get_product(product_id, user_id)
        current_count = await self._count_images(product_id)

        if current_count + len(files) > MAX_IMAGES_PER_PRODUCT:
            raise ValidationError(
                f"Maximum {MAX_IMAGES_PER_PRODUCT} images per product. "
                f"Currently {current_count}, trying to add {len(files)}."
            )

        upload_dir = self._product_upload_dir(product_id)
        results = []

        for i, file in enumerate(files):
            # Validate extension
            ext = os.path.splitext(file.filename or "")[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(
                    f"File '{file.filename}' has unsupported type '{ext}'. "
                    f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                )

            # Validate size
            content = await file.read()
            max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
            if len(content) > max_bytes:
                raise ValidationError(
                    f"File '{file.filename}' exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit."
                )

            # Save file
            file_id = uuid.uuid4()
            saved_filename = f"{file_id}{ext}"
            file_path = upload_dir / saved_filename
            with open(file_path, "wb") as f:
                f.write(content)

            # Determine if this should be primary (first image of product)
            is_primary = (current_count == 0 and i == 0)
            sort_order = current_count + i

            # URL path relative to the uploads mount
            url = f"/uploads/products/{product_id}/{saved_filename}"

            image = ProductImage(
                product_id=product_id,
                url=url,
                filename=file.filename or saved_filename,
                image_type=image_type,
                sort_order=sort_order,
                is_primary=is_primary,
                is_ai_generated=False,
            )
            self.db.add(image)
            await self.db.flush()
            await self.db.refresh(image)

            results.append({
                "id": str(image.id),
                "url": image.url,
                "filename": image.filename,
                "image_type": image.image_type,
                "sort_order": image.sort_order,
                "is_primary": image.is_primary,
            })

        return results

    async def delete_image(
        self, user_id: uuid.UUID, product_id: uuid.UUID, image_id: uuid.UUID
    ) -> bool:
        """Delete a product image."""
        await self._get_product(product_id, user_id)

        result = await self.db.execute(
            select(ProductImage).where(
                ProductImage.id == image_id,
                ProductImage.product_id == product_id,
            )
        )
        image = result.scalar_one_or_none()
        if not image:
            raise NotFoundError("Image", str(image_id))

        # Delete file from disk
        file_path = Path(settings.UPLOAD_DIR) / image.url.lstrip("/uploads/")
        if file_path.exists():
            file_path.unlink()

        was_primary = image.is_primary
        await self.db.delete(image)
        await self.db.flush()

        # If deleted image was primary, make the first remaining image primary
        if was_primary:
            remaining = await self.db.execute(
                select(ProductImage)
                .where(ProductImage.product_id == product_id)
                .order_by(ProductImage.sort_order)
                .limit(1)
            )
            first = remaining.scalar_one_or_none()
            if first:
                first.is_primary = True
                await self.db.flush()

        return True

    async def reorder_images(
        self, user_id: uuid.UUID, product_id: uuid.UUID, image_ids: list[uuid.UUID]
    ) -> list[dict]:
        """Reorder images by providing an ordered list of image IDs."""
        await self._get_product(product_id, user_id)

        result = await self.db.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.sort_order)
        )
        images = {img.id: img for img in result.scalars().all()}

        for idx, img_id in enumerate(image_ids):
            if img_id in images:
                images[img_id].sort_order = idx

        await self.db.flush()

        ordered = sorted(images.values(), key=lambda x: x.sort_order)
        return [
            {
                "id": str(img.id),
                "url": img.url,
                "filename": img.filename,
                "sort_order": img.sort_order,
                "is_primary": img.is_primary,
            }
            for img in ordered
        ]

    async def set_primary(
        self, user_id: uuid.UUID, product_id: uuid.UUID, image_id: uuid.UUID
    ) -> dict:
        """Set a specific image as the primary image."""
        await self._get_product(product_id, user_id)

        # Unset all primary flags for this product
        await self.db.execute(
            update(ProductImage)
            .where(ProductImage.product_id == product_id)
            .values(is_primary=False)
        )

        # Set the target image as primary
        result = await self.db.execute(
            select(ProductImage).where(
                ProductImage.id == image_id,
                ProductImage.product_id == product_id,
            )
        )
        image = result.scalar_one_or_none()
        if not image:
            raise NotFoundError("Image", str(image_id))

        image.is_primary = True
        await self.db.flush()
        await self.db.refresh(image)

        return {
            "id": str(image.id),
            "url": image.url,
            "filename": image.filename,
            "is_primary": True,
        }

    async def get_images(self, user_id: uuid.UUID, product_id: uuid.UUID) -> list[dict]:
        """Get all images for a product."""
        await self._get_product(product_id, user_id)

        result = await self.db.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.sort_order)
        )
        images = result.scalars().all()

        return [
            {
                "id": str(img.id),
                "url": img.url,
                "filename": img.filename,
                "image_type": img.image_type,
                "sort_order": img.sort_order,
                "is_primary": img.is_primary,
                "is_ai_generated": img.is_ai_generated,
                "created_at": img.created_at.isoformat() if img.created_at else None,
            }
            for img in images
        ]
