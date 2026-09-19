"""Tests for product endpoints."""

import pytest
from httpx import AsyncClient


class TestProductCRUD:
    """Test product CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_product(self, client: AsyncClient, auth_headers):
        response = await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={
                "sku": "LED-STAR-001",
                "product_name": "Red Star LED Light for Bike and Car",
                "brand": "RedStar",
                "price": 299.00,
                "mrp": 499.00,
                "stock": 150,
                "color": "Red",
                "description": "High quality LED light suitable for bikes and cars.",
                "bullet_points": [
                    "Bright LED illumination",
                    "Universal fit for bikes and cars",
                    "Waterproof design",
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == "LED-STAR-001"
        assert data["product_name"] == "Red Star LED Light for Bike and Car"
        assert data["status"] == "draft"

    @pytest.mark.asyncio
    async def test_create_product_duplicate_sku(self, client: AsyncClient, auth_headers):
        # Create first
        await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={
                "sku": "DUP-001",
                "product_name": "Product One",
            },
        )
        # Try duplicate
        response = await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={
                "sku": "DUP-001",
                "product_name": "Product Two",
            },
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_list_products(self, client: AsyncClient, auth_headers):
        # Create a product first
        await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={"sku": "LIST-001", "product_name": "Test Product"},
        )

        response = await client.get("/api/v1/products", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_product(self, client: AsyncClient, auth_headers):
        # Create
        create_resp = await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={"sku": "GET-001", "product_name": "Get Test Product"},
        )
        product_id = create_resp.json()["id"]

        # Get
        response = await client.get(f"/api/v1/products/{product_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["sku"] == "GET-001"

    @pytest.mark.asyncio
    async def test_update_product(self, client: AsyncClient, auth_headers):
        # Create
        create_resp = await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={"sku": "UPD-001", "product_name": "Original Name"},
        )
        product_id = create_resp.json()["id"]

        # Update
        response = await client.put(
            f"/api/v1/products/{product_id}",
            headers=auth_headers,
            json={"product_name": "Updated Name", "price": 599.00},
        )
        assert response.status_code == 200
        assert response.json()["product_name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_product(self, client: AsyncClient, auth_headers):
        # Create
        create_resp = await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={"sku": "DEL-001", "product_name": "Delete Me"},
        )
        product_id = create_resp.json()["id"]

        # Delete
        response = await client.delete(f"/api/v1/products/{product_id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify deleted
        get_resp = await client.get(f"/api/v1/products/{product_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_search_products(self, client: AsyncClient, auth_headers):
        await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={"sku": "SRCH-001", "product_name": "LED Light Flashlight"},
        )
        await client.post(
            "/api/v1/products",
            headers=auth_headers,
            json={"sku": "SRCH-002", "product_name": "Phone Case Cover"},
        )

        response = await client.get(
            "/api/v1/products?search=LED", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all("LED" in item["product_name"].upper() or "LED" in item["sku"].upper() for item in data["items"])

    @pytest.mark.asyncio
    async def test_products_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/v1/products")
        assert response.status_code == 422
