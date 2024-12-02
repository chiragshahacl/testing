import json
from uuid import UUID

import pytest
import respx
from httpx import Response

from src.common.clients.patient.schemas import BedResourcesSchema
from src.common.clients.patient.services import PatientService
from src.settings import config
from tests.factories.patient import BedFactory, PatientFactory


@pytest.mark.asyncio
@respx.mock
async def test_get_beds_returns_bed_resources_schema():
    bed_group_id = UUID("32f1f5aa-5f7f-48c7-bb54-681e475cea56")
    expected_patient = PatientFactory.build()
    expected_bed = BedFactory.build(patient=expected_patient)
    respx.get(f"{config.WEB_BASE_URL}/bed-group/{bed_group_id}/beds").mock(
        return_value=Response(
            status_code=200,
            json={"resources": [json.loads(expected_bed.model_dump_json(by_alias=True))]},
        )
    )
    patient_service = PatientService(auth_token="valid_auth_token")

    result = await patient_service.get_beds(group_id=bed_group_id)

    assert (
        result.model_dump_json() == BedResourcesSchema(resources=[expected_bed]).model_dump_json()
    )
