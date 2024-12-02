import json
from uuid import uuid4

import pytest
from test_tools import assert_deep_equal

from src.common.clients.patient.http_client import PlatformHttpClient
from src.common.clients.patient.schemas import PatientSchema


@pytest.mark.asyncio
async def test_http_client():
    token = "some-valid-token"
    platform_client = PlatformHttpClient(auth_token=token)
    async with platform_client() as http_client:
        assert http_client is not None
        assert http_client.headers["Authorization"] == f"Bearer {token}"
        assert http_client.headers["Content-Type"] == "application/json"


def test_patient_schema_keeps_secrets():
    id = uuid4()
    instance = PatientSchema(
        id=id,
        primaryIdentifier="pm-id1",
        active=True,
        givenName="Jane",
        familyName="Doe",
        gender="female",
    )

    assert "Jane" not in str(instance)
    assert "Doe" not in str(instance)

    assert "Jane" not in instance.model_dump().values()
    assert "Doe" not in instance.model_dump().values()

    assert "Jane" not in repr(instance)
    assert "Doe" not in repr(instance)


def test_patient_schema_reveals_secrets_on_json_dump():
    id = uuid4()
    instance = PatientSchema(
        id=id,
        primaryIdentifier="pm-id1",
        active=True,
        givenName="Jane",
        familyName="Doe",
        gender="female",
    )

    assert_deep_equal(
        json.loads(instance.model_dump_json()),
        {
            "id": str(id),
            "primary_identifier": "pm-id1",
            "active": True,
            "given_name": "Jane",
            "family_name": "Doe",
            "gender": "female",
        },
    )
