import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User",
        "phone_number": "+1234567890",
        "birth_date": "1990-01-01",
    }


@pytest.mark.asyncio
async def test_register(sample_user_data):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/auth/register", json=sample_user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}


@pytest.mark.asyncio
async def test_register_duplicated(sample_user_data):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/auth/register", json=sample_user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/auth/register", json=sample_user_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Registration error"}
