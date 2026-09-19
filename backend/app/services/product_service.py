"""Product service."""

import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.product import Product
from app.models.user import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.product import (
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
)


class ProductService:
    """Product business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.audit_repo = AuditRepository(db)

    async def create_product(self, user: User, data: ProductCreateRequest) -> ProductResponse:
        """Create a new product."""
        if await self.product_repo.sku_exists(data.sku):
            raise ConflictError(f"A product with SKU '{data.sku}' already exists")

        product_data = data.model_dump(exclude_none=True)
        product_data["user_id"] = user.id

        product = await self.product_repo.create(product_data)

        # Audit log
        await self.audit_repo.log_action(
            user_id=user.id,
            action="product_created",
            entity_type="product",
            entity_id=product.id,
            new_value={"sku": product.sku, "name": product.product_name},
        )

        return ProductResponse.model_validate(product)

    async def get_product(self, user: User, product_id: uuid.UUID) -> ProductResponse:
        """Get a single product by ID."""
        product = await self.product_repo.get_by_id_with_relations(product_id)

        if product is None or product.user_id != user.id:
            raise NotFoundError("Product", str(product_id))

        response = ProductResponse.model_validate(product)
        # Count associated listings
        from app.repositories.listing_repo import ListingRepository
        listing_repo = ListingRepository(self.db)
        response.listing_count = await listing_repo.count_by_marketplace_status(
            user_id=user.id
        )
        return response

    async def update_product(
        self, user: User, product_id: uuid.UUID, data: ProductUpdateRequest
    ) -> ProductResponse:
        """Update an existing product."""
        product = await self.product_repo.get_by_id_with_relations(product_id)

        if product is None or product.user_id != user.id:
            raise NotFoundError("Product", str(product_id))

        update_data = data.model_dump(exclude_unset=True)

        # Check SKU uniqueness if being changed
        if "sku" in update_data and update_data["sku"] != product.sku:
            if await self.product_repo.sku_exists(update_data["sku"], exclude_id=product_id):
                raise ConflictError(f"A product with SKU '{update_data['sku']}' already exists")

        old_name = product.product_name
        for key, value in update_data.items():
            setattr(product, key, value)

        await self.db.flush()
        await self.db.refresh(product)

        await self.audit_repo.log_action(
            user_id=user.id,
            action="product_updated",
            entity_type="product",
            entity_id=product.id,
            old_value={"name": old_name},
            new_value={"name": product.product_name},
        )

        return ProductResponse.model_validate(product)

    async def delete_product(self, user: User, product_id: uuid.UUID) -> bool:
        """Soft-delete a product."""
        product = await self.product_repo.get_by_id(product_id)

        if product is None or product.user_id != user.id:
            raise NotFoundError("Product", str(product_id))

        await self.product_repo.soft_delete(product_id)

        await self.audit_repo.log_action(
            user_id=user.id,
            action="product_deleted",
            entity_type="product",
            entity_id=product_id,
            old_value={"sku": product.sku, "name": product.product_name},
        )

        return True

    async def list_products(
        self,
        user: User,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        status: str | None = None,
        category_id: uuid.UUID | None = None,
    ) -> ProductListResponse:
        """List products with search, filtering, and pagination."""
        offset = (page - 1) * page_size

        products, total = await self.product_repo.list_for_user(
            user_id=user.id,
            offset=offset,
            limit=page_size,
            search=search,
            status=status,
            category_id=category_id,
        )

        return ProductListResponse(
            items=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        )
