import uuid

import respx
from behave import step, when
from httpx import Response
from starlette import status

from features.steps.common import generate_valid_jwt_token
from src.bed_group.schemas import WebBedGroupResources
from src.settings import settings


@step("bed groups are found")
def step_impl(context):
    context.group_id = uuid.uuid4()
    context.group_name = "Room I"
    context.group_description = "The room next to the other room"
    context.expected_response = {
        "resources": [
            {
                "id": str(context.group_id),
                "name": context.group_name,
                "description": context.group_description,
                "beds": [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Awesome bed",
                        "patient": None,
                    }
                ],
            }
        ]
    }


@step("a request to get a bed group list")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.request = {
        "headers": {
            "Authorization": context.valid_token,
            "Content-Type": "application/json",
        },
        "url": "/web/bed-group",
    }
    context.expected_code = status.HTTP_200_OK


@when("the request is made to get a bed group list")
def step_impl(context):
    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group",
        headers=context.request.get("headers"),
    ).mock(
        return_value=Response(
            status_code=context.expected_code,
            json=context.expected_response,
        )
    )
    context.response = context.client.get(**context.request)


@step("a bed group list is returned")
def step_impl(context):
    bed_group_response = WebBedGroupResources(**context.response.json())
    expected_response = WebBedGroupResources(**context.expected_response)
    assert bed_group_response == expected_response


@step("an empty bed group list is returned")
def step_impl(context):
    resp = context.response.json()
    assert not resp["resources"]


@step("bed groups not found")
def step_impl(context):
    context.expected_response = {"resources": []}
