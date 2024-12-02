import uuid
from uuid import UUID

import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to get bed group observations")
def step_impl(context):
    context.group_id = (
        "eb9b3908-2ec1-4182-b739-1233f7c4eb38"  # Corrected to match the failing request
    )
    context.request = {
        "url": f"/web/bed-group/{context.group_id}/alerts",
    }
    context.expected_code = status.HTTP_200_OK


@step("several patients exist within the bed group")
def step_impl(context):
    context.patient_ids = [
        UUID("784bd1a1-92df-4bd3-bcb6-e5ce210d5f1d"),
        UUID("64d3392e-68a0-426a-8051-3eaace6ef58c"),
    ]
    context.bed_resources = [
        {
            "id": "01ff7fe2-0414-43a3-a607-7cdd596e695b",
            "name": "Bed1",
            "patient": {
                "id": str(context.patient_ids[0]),
                "primary_identifier": "PID-1",
                "active": True,
                "family_name": "Walsh",
                "given_name": "Declan",
                "gender": "male",
                "birth_date": "1997-03-29",
            },
            "encounter": None,
        },
        {
            "id": "994c8fae-03b8-46ea-b3d7-d3ff472c6d05",
            "name": "Bed2",
            "patient": {
                "id": str(context.patient_ids[1]),
                "primary_identifier": "PID-2",
                "active": True,
                "family_name": "Walsh",
                "given_name": "Coleman",
                "gender": "male",
                "birth_date": "1999-06-21",
            },
            "encounter": None,
        },
    ]
    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/{context.group_id}/beds",
    ).mock(
        return_value=Response(
            status_code=context.expected_code,
            json={
                "resources": context.bed_resources,
            },
        )
    )


@step("the patients have some observations")
def step_impl(context):
    context.observation_resources = [
        {
            "id": "568fa11d-8269-43a7-a00c-be6489431d5f",
            "category": "cat1",
            "code": "code1",
            "subject_id": "784bd1a1-92df-4bd3-bcb6-e5ce210d5f1d",
            "effective_dt": "2023-06-28 15:57:05.100669",
            "value_number": 79.2,
            "value_text": "heart rate",
            "device_primary_identifier": str(uuid.uuid4()),
            "device_code": "device-code",
        },
        {
            "id": "56aadd8f-fbd7-4c1c-b1b1-18abd8cc575b",
            "category": "cat1",
            "code": "code1",
            "subject_id": "784bd1a1-92df-4bd3-bcb6-e5ce210d5f1d",
            "effective_dt": "2023-06-28 15:55:05.100669",
            "value_number": 79.2,
            "value_text": "heart rate",
            "device_primary_identifier": str(uuid.uuid4()),
            "device_code": "device-code",
        },
        {
            "id": "fb730db8-b25f-43c2-8bf2-e7ce6b0e967a",
            "category": "cat1",
            "code": "code1",
            "subject_id": "64d3392e-68a0-426a-8051-3eaace6ef58c",
            "effective_dt": "2023-06-28 15:57:05.100669",
            "value_number": 79.2,
            "value_text": "heart rate",
            "device_primary_identifier": str(uuid.uuid4()),
            "device_code": "device-code",
        },
        {
            "id": "e8fbc089-89f2-464a-99c1-1b70c1880bca",
            "category": "cat1",
            "code": "code1",
            "subject_id": "64d3392e-68a0-426a-8051-3eaace6ef58c",
            "effective_dt": "2023-06-28 15:55:05.100669",
            "value_number": 79.2,
            "value_text": "heart rate",
            "device_primary_identifier": str(uuid.uuid4()),
            "device_code": "device-code",
        },
    ]

    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/observation",
        params={
            "patientIds": context.patient_ids,
            "isAlert": True,
        },
    ).mock(
        return_value=Response(
            status_code=context.expected_code,
            json={"resources": context.observation_resources},
        )
    )


@step("patients doesn't exist within the bed group")
def step_impl(context):
    context.patient_ids = []
    context.group_id = "eb9b3908-2ec1-4182-b739-1233f7c4eb38"
    context.bed_resources = [
        {
            "id": "01ff7fe2-0414-43a3-a607-7cdd596e6951",
            "name": "Bed1",
            "patient": {},
        },
        {
            "id": "994c8fae-03b8-46ea-b3d7-d3ff472c6d02",
            "name": "Bed2",
            "patient": {},
        },
    ]

    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/{context.group_id}/beds",
    ).mock(
        return_value=Response(
            status_code=context.expected_code,
            json={
                "resources": context.bed_resources,
            },
        )
    )


@step("a request to get empty bed group observations")
def step_impl(context):
    context.group_id = "eb9b3908-2ec1-4182-b739-1233f7c4eb38"
    context.request = {
        "url": f"/web/bed-group/{context.group_id}/alerts",
    }
    context.expected_code = status.HTTP_200_OK


@step("the patients does not have any observations")
def step_impl(context):
    context.observation_resources = []

    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/observation",
        params={
            "patientIds": context.patient_ids,
            "isAlert": True,
        },
    ).mock(
        return_value=Response(
            status_code=context.expected_code,
            json={"resources": context.observation_resources},
        )
    )


@when("the request is made to get bed group observations")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("the empty bed groups observations are returned")
def step_impl(context):
    assert context.response.json()
    resp = context.response.json()
    assert len(resp["resources"]) == len(context.patient_ids)


@step("the bed groups observations are returned")
def step_impl(context):
    assert context.response.json()
    resp = context.response.json()
    assert len(resp["resources"]) == len(context.patient_ids)
    for index, patient_id in enumerate(context.patient_ids):
        item = resp["resources"][index]
        patient = context.bed_resources[index]["patient"]
        expected_observations = [
            obs for obs in context.observation_resources if obs["subject_id"] == str(patient_id)
        ]
        assert item["patientId"] == str(patient_id)
        assert item["primaryIdentifier"] == patient["primary_identifier"]
        assert len(item["alerts"]) == len(expected_observations)
        for alert_index, alert in enumerate(item["alerts"]):
            expected_obs = expected_observations[alert_index]
            assert alert["id"] == expected_obs["id"]
            assert alert["category"] == expected_obs["category"]
            assert alert["code"] == expected_obs["code"]
            assert alert["valueNumber"] == str(expected_obs["value_number"])
            assert alert["valueText"] == expected_obs["value_text"]
            assert alert["deviceCode"] == expected_obs["device_code"]
            assert alert["devicePrimaryIdentifier"] == expected_obs["device_primary_identifier"]
