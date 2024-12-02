import json
from uuid import uuid4

import httpx
import pytest
import respx
from httpx import Response

from src.common.platform.patient import client
from src.common.platform.patient.schemas import CreatePatientSchema, UpsertPatientSchema
from src.settings import settings

root_url: str = f"{settings.PATIENT_PLATFORM_BASE_URL}"


@pytest.mark.asyncio
async def test_get_patient_by_identifier(respx_mock):
    identifier = "p-id1"
    id = uuid4()
    response = {
        "id": str(id),
        "primary_identifier": identifier,
        "active": True,
        "given_name": "John",
        "family_name": "Doe",
        "gender": "male",
    }
    respx_mock.get(f"{root_url}/identifier/{identifier}").mock(
        return_value=Response(200, text=json.dumps(response))
    )

    response = await client.PatientPlatformClient(httpx.AsyncClient()).get_patient_by_identifier(
        identifier
    )

    assert response.primary_identifier == identifier
    assert response.id == id
    assert response.active is True
    assert response.given_name.get_secret_value() == "John"
    assert response.family_name.get_secret_value() == "Doe"
    assert response.gender == "male"


@pytest.mark.asyncio
async def test_get_patient_by_id(respx_mock):
    id = uuid4()
    response = {
        "id": str(id),
        "primary_identifier": "p-id1",
        "active": True,
        "given_name": "John",
        "family_name": "Doe",
        "gender": "male",
    }
    respx_mock.get(f"{root_url}/{id}").mock(return_value=Response(200, text=json.dumps(response)))

    response = await client.PatientPlatformClient(httpx.AsyncClient()).get_patient_by_id(id)

    assert response.primary_identifier == "p-id1"
    assert response.id == id
    assert response.active is True
    assert response.given_name.get_secret_value() == "John"
    assert response.family_name.get_secret_value() == "Doe"
    assert response.gender == "male"


@pytest.mark.asyncio
async def test_get_patients(respx_mock):
    id = uuid4()
    response = {
        "resources": [
            {
                "id": str(id),
                "primary_identifier": "p-id1",
                "active": True,
                "given_name": "John",
                "family_name": "Doe",
                "gender": "male",
            }
        ]
    }
    respx_mock.get(f"{root_url}").mock(return_value=Response(200, text=json.dumps(response)))

    response = await client.PatientPlatformClient(httpx.AsyncClient()).get_patients()

    assert response.resources
    for patient in response.resources:
        assert patient.primary_identifier == "p-id1"
        assert patient.id == id
        assert patient.active is True
        assert patient.given_name.get_secret_value() == "John"
        assert patient.family_name.get_secret_value() == "Doe"
        assert patient.gender == "male"


@pytest.mark.asyncio
async def test_create_patient(respx_mock):
    id = uuid4()
    patient = {
        "id": str(id),
        "primary_identifier": "p-id1",
        "active": True,
        "given_name": "John",
        "family_name": "Doe",
        "gender": "male",
        "birth_date": None,
    }
    payload = CreatePatientSchema(**patient)
    respx_mock.post(f"{root_url}/CreatePatient").mock(
        return_value=Response(200, text=json.dumps(patient))
    )

    response = await client.PatientPlatformClient(httpx.AsyncClient()).create_patient(payload)

    last_request = respx.calls.last.request
    assert json.loads(last_request.content) == patient
    assert response.primary_identifier == "p-id1"
    assert response.id == id
    assert response.active is True
    assert response.given_name.get_secret_value() == "John"
    assert response.family_name.get_secret_value() == "Doe"
    assert response.gender == "male"


@pytest.mark.asyncio
async def test_update_patient(respx_mock):
    id = uuid4()
    patient = {
        "id": str(id),
        "primary_identifier": "p-id1",
        "active": True,
        "given_name": "John",
        "family_name": "Doe",
        "gender": "male",
        "birth_date": None,
    }
    payload = UpsertPatientSchema(**patient)
    respx_mock.post(f"{root_url}/UpdatePatientInfo").mock(
        return_value=Response(200, text=json.dumps(patient))
    )

    response = await client.PatientPlatformClient(httpx.AsyncClient()).update_patient(payload)

    last_request = respx.calls.last.request
    assert json.loads(last_request.content) == patient
    assert response.primary_identifier == "p-id1"
    assert response.id == id
    assert response.active is True
    assert response.given_name.get_secret_value() == "John"
    assert response.family_name.get_secret_value() == "Doe"
    assert response.gender == "male"
