import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def async_client():
    """Async client for testing the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def token(async_client):
    """Get a token for authentication."""
    await async_client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User",
            "phone_number": "+351919999999",
            "birth_date": "1990-01-01",
        },
    )
    return (
        await async_client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
    ).json()["token"]
