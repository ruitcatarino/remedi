import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def token(async_client):
    await async_client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User",
            "phone_number": "+1234567890",
            "birth_date": "1990-01-01",
        },
    )
    return (
        await async_client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
    ).json()["token"]


@pytest.fixture
def sample_person_data():
    """Sample person data for testing."""
    return {
        "name": "Test Person",
        "birth_date": "1990-01-01",
        "notes": "Test notes",
    }


@pytest.fixture
def list_persons_data():
    """A list of persons data for testing."""
    return [
        {
            "name": "Test Person",
            "birth_date": "1990-01-01",
            "notes": "Test notes",
        },
        {
            "name": "Test Person2",
            "birth_date": "1999-01-01",
        },
    ]


@pytest.mark.asyncio
async def test_register_person(async_client, token, sample_person_data):
    response = await async_client.post(
        "/person/register",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}


@pytest.mark.asyncio
async def test_register_person_duplicated(async_client, token, sample_person_data):
    response = await async_client.post(
        "/person/register",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}

    response = await async_client.post(
        "/person/register",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person registration error"}


@pytest.mark.asyncio
async def test_list_persons(async_client, token, list_persons_data):
    for person in list_persons_data:
        response = await async_client.post(
            "/person/register",
            json=person,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Person registered successfully"}

    response = await async_client.get(
        "/person/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    for i, person in enumerate(list_persons_data):
        assert response_data[i] == {
            "id": i + 1,
            "name": person["name"],
            "birth_date": person["birth_date"],
            "notes": person.get("notes"),
        }
