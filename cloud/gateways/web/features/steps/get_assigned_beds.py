import uuid
from datetime import datetime

import respx
from behave import step, then, when
from httpx import Response
from starlette import status

from features.steps.common import generate_valid_jwt_token
from src.bed.schemas import WebBedResources
from src.settings import settings


@step("a bed group exists")
def step_impl(context):
    context.group_id = uuid.uuid4()


@step("no bed group exists")
def step_impl(context):
    context.group_id = uuid.uuid4()
    context.expected_code = status.HTTP_200_OK
    context.expected_response = {"resources": []}


@step("a bed assigned to the group")
def step_impl(context):
    context.bed_id = uuid.uuid4()
    context.bed_name = "Bed II"
    context.expected_response = {
        "resources": [
            {
                "id": str(context.bed_id),
                "name": context.bed_name,
                "patient": {
                    "id": "e10cfe59-c3c1-42b6-b2b9-d11350a01ceb",
                    "primary_identifier": "PX-001",
                    "active": True,
                    "given_name": "Alf",
                    "family_name": "Perez",
                    "gender": "male",
                    "birth_date": "2015-12-15",
                },
                "encounter": {
                    "id": "09de618f-ee72-4a7b-96af-24b74593b0ef",
                    "subject_id": "e10cfe59-c3c1-42b6-b2b9-d11350a01ceb",
                    "device_id": "0909bf08-4189-42a8-a4b5-16f7191b26dc",
                    "created_at": datetime(2024, 1, 15, 15, 0, 0).isoformat(),
                    "status": "in-progress",
                    "start_time": datetime(2024, 1, 15, 15, 0, 0).isoformat(),
                    "end_time": None,
                },
            }
        ]
    }
    context.expected_code = status.HTTP_200_OK


@step("a request to get assigned beds for the group")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.request = {
        "headers": {
            "Authorization": context.valid_token,
            "Content-Type": "application/json",
        },
        "url": f"/web/bed-group/{context.group_id}/beds",
    }


@when("the request is made to get assigned beds for a group")
def step_impl(context):
    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/{context.group_id}/beds",
        headers=context.request.get("headers"),
    ).mock(
        return_value=Response(
            status_code=context.expected_code,
            json=context.expected_response,
        )
    )
    context.response = context.client.get(**context.request)


@step("a list of bed is returned")
def step_impl(context):
    beds_response = WebBedResources(**context.response.json())
    expected_response = WebBedResources(**context.expected_response)
    assert beds_response == expected_response


@then("an empty bed list is returned")
def step_impl(context):
    resp = context.response.json()
    assert not resp["resources"]
