"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


class TestAuthSignup:
    """Test signup endpoint."""

    @pytest.mark.asyncio
    async def test_signup_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "new@seller.com",
                "password": "securepassword123",
                "full_name": "New Seller",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert "tokens" in data
        assert data["user"]["email"] == "new@seller.com"
        assert data["tokens"]["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "securepassword123",
                "full_name": "Duplicate Seller",
            },
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_signup_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "not-an-email",
                "password": "securepassword123",
                "full_name": "Bad Email",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_signup_short_password(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "short@pass.com",
                "password": "short",
                "full_name": "Short Pass",
            },
        )
        assert response.status_code == 422


class TestAuthLogin:
    """Test login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "tokens" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_email(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "ghost@example.com",
                "password": "anypassword123",
            },
        )
        assert response.status_code == 401


class TestAuthMe:
    """Test user profile endpoints."""

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, client: AsyncClient, auth_headers):
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 422  # Missing Authorization header

    @pytest.mark.asyncio
    async def test_update_me(self, client: AsyncClient, auth_headers):
        response = await client.put(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"full_name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"
