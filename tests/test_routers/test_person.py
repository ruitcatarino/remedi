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
def sample_person_list_data():
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


async def _register_person(async_client, token, sample_person_data):
    return await async_client.post(
        "/person/register",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.mark.asyncio
async def test_register_person(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}


@pytest.mark.asyncio
async def test_register_person_duplicated(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}

    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Person registration error"}


@pytest.mark.asyncio
async def test_register_person_invalid_token(async_client, sample_person_data):
    response = await _register_person(async_client, "invalid_token", sample_person_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed"}


@pytest.mark.asyncio
async def test_list_persons(async_client, token, sample_person_list_data):
    for person in sample_person_list_data:
        response = await _register_person(async_client, token, person)
        assert response.status_code == 200
        assert response.json() == {"message": "Person registered successfully"}

    response = await async_client.get(
        "/person/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    for i, person in enumerate(sample_person_list_data):
        assert response_data[i] == {
            "id": i + 1,
            "name": person["name"],
            "birth_date": person["birth_date"],
            "notes": person.get("notes"),
        }


@pytest.mark.asyncio
async def test_list_persons_empty(async_client, token):
    response = await async_client.get(
        "/person/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_get_person(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}

    response = await async_client.get(
        f"/person/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == sample_person_data | {"id": 1}


@pytest.mark.asyncio
async def test_get_person_invalid(async_client, token, sample_person_data):
    response = await async_client.get(
        f"/person/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_get_person_by_name(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}

    response = await async_client.get(
        f"/person/name/{sample_person_data['name']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == sample_person_data | {"id": 1}


@pytest.mark.asyncio
async def test_update_person(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}

    sample_person_data["name"] = "Updated Name"
    sample_person_data["birth_date"] = "2000-01-01"
    sample_person_data["notes"] = "Updated notes"
    response = await async_client.put(
        f"/person/{1}",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == sample_person_data | {"id": 1}

    response = await async_client.get(
        f"/person/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == sample_person_data | {"id": 1}


@pytest.mark.asyncio
async def test_update_person_invalid(async_client, token, sample_person_data):
    response = await async_client.put(
        f"/person/{1}",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_update_person_by_name(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}

    old_name = sample_person_data["name"]
    sample_person_data["name"] = "Updated Name"
    sample_person_data["birth_date"] = "2000-01-01"
    sample_person_data["notes"] = "Updated notes"
    response = await async_client.put(
        f"/person/name/{old_name}",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == sample_person_data | {"id": 1}

    response = await async_client.get(
        f"/person/name/{sample_person_data['name']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == sample_person_data | {"id": 1}

    response = await async_client.get(
        f"/person/name/{old_name}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_update_person_by_name_invalid(async_client, token, sample_person_data):
    response = await async_client.put(
        f"/person/name/{sample_person_data['name']}",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_delete_persons(async_client, token, sample_person_list_data):
    for person in sample_person_list_data:
        response = await _register_person(async_client, token, person)
        assert response.status_code == 200
        assert response.json() == {"message": "Person registered successfully"}

    response = await async_client.delete(
        "/person/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Persons deleted successfully"}

    response = await async_client.get(
        "/person/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_delete_persons_invalid(async_client, token):
    response = await async_client.delete(
        "/person/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_delete_person(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}

    response = await async_client.delete(
        f"/person/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Person deleted successfully"}

    response = await async_client.get(
        f"/person/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_delete_person_invalid(async_client, token, sample_person_data):
    response = await async_client.delete(
        f"/person/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_delete_person_by_name(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Person registered successfully"}

    response = await async_client.delete(
        f"/person/name/{sample_person_data['name']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Person deleted successfully"}

    response = await async_client.get(
        f"/person/name/{sample_person_data['name']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_delete_person_by_name_invalid(async_client, token, sample_person_data):
    response = await async_client.delete(
        f"/person/name/{sample_person_data['name']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}
