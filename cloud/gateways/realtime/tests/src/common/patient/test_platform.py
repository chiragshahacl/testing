import json
from uuid import UUID

import pytest
import respx
from httpx import Response

from src.common.clients.patient.http_client import PlatformHttpClient
from src.common.clients.patient.platform import PatientPlatformClient
from src.common.clients.patient.schemas import BedResourcesSchema
from tests.factories.patient import BedFactory, PatientFactory


@pytest.mark.asyncio
@respx.mock
async def test_get_beds_by_group_id_patient_assigned():
    bed_group_id = UUID("db3e61da-c62f-4325-84fe-03697da4fc3b")
    http_client = PlatformHttpClient("valid_auth_token")
    patient_client = PatientPlatformClient(http_client)
    expected_patient = PatientFactory.build()
    expected_bed = BedFactory.build(patient=expected_patient)
    respx.get(f"{patient_client.root_url}/bed-group/{bed_group_id}/beds").mock(
        return_value=Response(
            status_code=200,
            json={"resources": [json.loads(expected_bed.model_dump_json(by_alias=True))]},
        )
    )

    result = await patient_client.get_beds_by_group_id(bed_group_id)

    assert (
        result.model_dump_json() == BedResourcesSchema(resources=[expected_bed]).model_dump_json()
    )


@pytest.mark.asyncio
@respx.mock
async def test_get_beds_by_group_id_patient_not_assigned():
    bed_group_id = UUID("db3e61da-c62f-4325-84fe-03697da4fc3b")
    http_client = PlatformHttpClient("valid_auth_token")
    patient_client = PatientPlatformClient(http_client)
    expected_bed = BedFactory.build(patient=None)
    respx.get(f"{patient_client.root_url}/bed-group/{bed_group_id}/beds").mock(
        return_value=Response(
            status_code=200,
            json={"resources": [json.loads(expected_bed.model_dump_json(by_alias=True))]},
        )
    )

    result = await patient_client.get_beds_by_group_id(bed_group_id)

    assert (
        result.model_dump_json() == BedResourcesSchema(resources=[expected_bed]).model_dump_json()
    )
