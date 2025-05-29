from datetime import datetime, timedelta

import pytest
import pytest_asyncio

from app.models.medication import Medication


@pytest_asyncio.fixture
async def token(async_client):
    """
    Register a test user, a test person and get a token for authentication.
    """
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
    token = (
        await async_client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
    ).json()["token"]
    # Register a test person
    await async_client.post(
        "/person/register",
        json={
            "name": "Test Person",
            "birth_date": "1990-01-01",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return token


@pytest.fixture
def sample_medication_data():
    """Sample medication data for testing."""
    return {
        "name": "Test Medication",
        "person_id": 1,
        "dosage": "20mg",
        "frequency": 1440,  # 1440 minutes = 1 day
        "start_date": (datetime.now() + timedelta(days=1)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "end_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


@pytest.fixture
def sample_medication_list_data():
    return [
        {
            "name": "Test Medication",
            "person_id": 1,
            "dosage": "20mg",
            "frequency": 1440,  # 1440 minutes = 1 day
            "start_date": (datetime.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "end_date": (datetime.now() + timedelta(days=2)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        },
        {
            "name": "Test Medication 2",
            "person_id": 1,
            "dosage": "100µg",
            "frequency": 360,  # 360 minutes = 6 hours
            "start_date": (datetime.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "total_doses": 3,
        },
    ]


async def _register_medication(async_client, token, medication_data):
    return await async_client.post(
        "/medication/register",
        json=medication_data,
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.mark.asyncio
async def test_register_medication(async_client, token, sample_medication_data):
    response = await _register_medication(async_client, token, sample_medication_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Medication registered successfully"}


@pytest.mark.asyncio
async def test_register_medication_no_start_date(
    async_client, token, sample_medication_data
):
    sample_medication_data.pop("start_date")
    response = await _register_medication(async_client, token, sample_medication_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Medication registered successfully"}
    medication = await Medication.get()
    assert medication.start_date is not None


@pytest.mark.asyncio
async def test_register_invalid_person(async_client, token):
    response = await _register_medication(
        async_client,
        token,
        {
            "name": "Test Medication",
            "person_id": 9999999,
            "dosage": "20mg",
            "frequency": 1440,
            "start_date": (datetime.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "end_date": (datetime.now() + timedelta(days=2)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Person not found"}


@pytest.mark.asyncio
async def test_register_medication_invalid_frequency(async_client, token):
    response = await _register_medication(
        async_client,
        token,
        {
            "name": "Test Medication",
            "person_id": 1,
            "dosage": "20mg",
            "frequency": "1440",  # frequency must be a int
            "start_date": (datetime.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "end_date": (datetime.now() + timedelta(days=2)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_medication_missing_data(async_client, token):
    """
    Test registering medication with missing data.
    Either `end_date` or `total_doses` must be provided for non-PRN medications.
    """
    response = await _register_medication(
        async_client,
        token,
        {
            "name": "Test Medication",
            "person_id": 1,
            "dosage": "20mg",
            "frequency": 1440,
            "start_date": (datetime.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        },
    )
    assert response.status_code == 422

    response = await _register_medication(
        async_client,
        token,
        {
            "name": "Test Medication",
            "person_id": 1,
            "dosage": "20mg",
            "start_date": (datetime.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "is_prn": True,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Medication registered successfully"}

    response = await _register_medication(
        async_client,
        token,
        {
            "name": "Test Medication 2",
            "person_id": 1,
            "dosage": "20mg",
            "frequency": 1440,
            "start_date": (datetime.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "end_date": (datetime.now() + timedelta(days=2)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Medication registered successfully"}

    response = await _register_medication(
        async_client,
        token,
        {
            "name": "Test Medication 3",
            "person_id": 1,
            "dosage": "20mg",
            "frequency": 1440,
            "start_date": (datetime.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "total_doses": 10,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Medication registered successfully"}


@pytest.mark.asyncio
async def test_get_medication(async_client, token, sample_medication_list_data):
    for medication in sample_medication_list_data:
        response = await _register_medication(async_client, token, medication)
        assert response.status_code == 200
        assert response.json() == {"message": "Medication registered successfully"}

    response = await async_client.get(
        "/medication/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    response_data = response.json()
    for i, medication in enumerate(sample_medication_list_data):
        assert medication["name"] == response_data[i]["name"]
        assert medication["person_id"] == response_data[i]["person"]["id"]
        assert medication["dosage"] == response_data[i]["dosage"]
        assert medication["frequency"] == response_data[i]["frequency"]
        assert medication["start_date"] == response_data[i]["start_date"]
        assert medication.get("end_date") == response_data[i]["end_date"]
        assert medication.get("total_doses") == response_data[i]["total_doses"]


@pytest.mark.asyncio
async def test_get_empty_medication(async_client, token):
    response = await async_client.get(
        "/medication/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Medication not found"}
