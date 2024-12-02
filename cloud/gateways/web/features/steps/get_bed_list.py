import uuid

import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.bed.schemas import WebBedResources
from src.settings import settings


@step("beds are found")
def step_impl(context):
    context.bed_id = uuid.uuid4()
    context.bed_name = "Bed I"
    context.patient = None
    context.expected_response = {
        "resources": [
            {
                "id": str(context.bed_id),
                "name": context.bed_name,
                "patient": context.patient,
            }
        ]
    }


@step("beds not found")
def step_impl(context):
    context.expected_response = {"resources": []}


@step("a request to get a bed list")
def step_impl(context):
    context.request = {
        "url": "/web/bed",
    }
    context.expected_code = status.HTTP_200_OK


@when("the request is made to get a bed list")
def step_impl(context):
    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed",
        headers=context.request.get("headers"),
    ).mock(
        return_value=Response(
            status_code=context.expected_code,
            json=context.expected_response,
        )
    )
    context.response = context.client.get(**context.request)


@step("a bed list is returned")
def step_impl(context):
    bed_group_response = WebBedResources(**context.response.json())
    expected_response = WebBedResources(**context.expected_response)
    assert bed_group_response == expected_response
