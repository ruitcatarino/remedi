import pytest


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
            "notes": "Some notes",
        },
    ]


async def _register_person(async_client, token, sample_person_data):
    return await async_client.post(
        "/persons/",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.mark.asyncio
async def test_register_person(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 201
    assert response.json() == sample_person_data | {"id": 1}


@pytest.mark.asyncio
async def test_register_person_duplicated(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 201
    assert response.json() == sample_person_data | {"id": 1}

    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 409
    assert response.json() == {
        "detail": f"Person with name '{sample_person_data['name']}' already exists"
    }


@pytest.mark.asyncio
async def test_register_person_invalid_token(async_client, sample_person_data):
    response = await _register_person(async_client, "invalid_token", sample_person_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication failed"}


@pytest.mark.asyncio
async def test_list_persons(async_client, token, sample_person_list_data):
    for id, person in enumerate(sample_person_list_data, start=1):
        response = await _register_person(async_client, token, person)
        assert response.status_code == 201
        assert response.json() == person | {"id": id}

    response = await async_client.get(
        "/persons/", headers={"Authorization": f"Bearer {token}"}
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
        "/persons/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    response.json() == []


@pytest.mark.asyncio
async def test_get_person(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 201
    assert response.json() == sample_person_data | {"id": 1}

    response = await async_client.get(
        f"/persons/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == sample_person_data | {"id": 1}


@pytest.mark.asyncio
async def test_get_person_invalid(async_client, token, sample_person_data):
    response = await async_client.get(
        f"/persons/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_update_person(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 201
    assert response.json() == sample_person_data | {"id": 1}

    sample_person_data["name"] = "Updated Name"
    sample_person_data["birth_date"] = "2000-01-01"
    sample_person_data["notes"] = "Updated notes"
    response = await async_client.put(
        f"/persons/{1}",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == sample_person_data | {"id": 1}

    response = await async_client.get(
        f"/persons/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == sample_person_data | {"id": 1}


@pytest.mark.asyncio
async def test_update_person_not_found(async_client, token, sample_person_data):
    response = await async_client.put(
        f"/persons/{1}",
        json=sample_person_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_invalid_update_person(async_client, token, sample_person_list_data):
    for id, person in enumerate(sample_person_list_data, start=1):
        response = await _register_person(async_client, token, person)
        assert response.status_code == 201
        assert response.json() == person | {"id": id}

    response = await async_client.put(
        f"/persons/{1}",
        json={"name": sample_person_list_data[1]["name"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Update failed due to constraint violation"}


@pytest.mark.asyncio
async def test_disable_person(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 201
    assert response.json() == sample_person_data | {"id": 1}

    response = await async_client.patch(
        "/persons/disable/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    response = await async_client.get(
        "/persons/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_disable_person_not_found(async_client, token):
    response = await async_client.patch(
        "/persons/disable/999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_enable_person(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 201
    assert response.json() == sample_person_data | {"id": 1}

    response = await async_client.patch(
        "/persons/disable/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    response = await async_client.get(
        "/persons/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == []

    response = await async_client.patch(
        "/persons/enable/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    response = await async_client.get(
        "/persons/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()[0] == {
        "id": 1,
        "name": sample_person_data["name"],
        "birth_date": sample_person_data["birth_date"],
        "notes": sample_person_data["notes"],
    }


@pytest.mark.asyncio
async def test_enable_person_not_found(async_client, token):
    response = await async_client.patch(
        "/persons/enable/999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_delete_person(async_client, token, sample_person_data):
    response = await _register_person(async_client, token, sample_person_data)
    assert response.status_code == 201
    assert response.json() == sample_person_data | {"id": 1}

    response = await async_client.delete(
        f"/persons/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Person '{sample_person_data['name']}' deleted successfully"
    }

    response = await async_client.get(
        f"/persons/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_delete_person_invalid(async_client, token, sample_person_data):
    response = await async_client.delete(
        f"/persons/{1}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}
