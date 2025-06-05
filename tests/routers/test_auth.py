import pytest

from app.models.user import User


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
async def test_register(async_client, sample_user_data):
    response = await async_client.post("/auth/register", json=sample_user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}


@pytest.mark.asyncio
async def test_register_duplicated(async_client, sample_user_data):
    response = await async_client.post("/auth/register", json=sample_user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    response = await async_client.post("/auth/register", json=sample_user_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Registration error"}


@pytest.mark.asyncio
async def test_login(async_client, sample_user_data):
    response = await async_client.post("/auth/register", json=sample_user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    response = await async_client.post(
        "/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "User logged in successfully",
        "token": response.json()["token"],
    }


@pytest.mark.asyncio
async def test_login_disabled(async_client, sample_user_data):
    response = await async_client.post("/auth/register", json=sample_user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    response = await async_client.post(
        "/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["token"]
    assert response.json() == {
        "message": "User logged in successfully",
        "token": token,
    }

    user = await User.from_jwt(token)
    user.disabled = True
    await user.save()

    response = await async_client.post(
        "/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Login error"}


@pytest.mark.asyncio
async def test_invalid_login(async_client):
    response = await async_client.post(
        "/auth/login",
        json={"email": "wrong_email@example.com", "password": "wrong_password"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Login error"}


@pytest.mark.asyncio
async def test_logout(async_client, sample_user_data):
    response = await async_client.post("/auth/register", json=sample_user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    response = await async_client.post(
        "/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["token"]
    assert response.json() == {"message": "User logged in successfully", "token": token}

    response = await async_client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": f"User {sample_user_data['email']} logged out successfully"
    }


@pytest.mark.asyncio
async def test_logout_with_blacklisted_token(async_client, sample_user_data):
    response = await async_client.post("/auth/register", json=sample_user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    response = await async_client.post(
        "/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["token"]
    assert response.json() == {"message": "User logged in successfully", "token": token}

    response = await async_client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": f"User {sample_user_data['email']} logged out successfully"
    }

    response = await async_client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Logout error"}


@pytest.mark.asyncio
async def test_logout_invalid_token(async_client):
    response = await async_client.post(
        "/auth/logout", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed"}
