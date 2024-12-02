import uuid

import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to assign some beds")
def step_impl(context):
    context.group_id = "945a67b8-d41d-4523-8dd7-773e8ade7e7d"
    context.payload = [str(uuid.uuid4()) for _ in range(3)]
    context.request = {
        "url": f"/web/bed-group/{context.group_id}/beds",
        "json": {
            "bed_ids": context.payload,
        },
    }


@step("the beds can be assigned")
def step_impl(context):
    respx.post(f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/BatchAssignBeds").mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    )


@step("the beds cant be assigned")
def step_impl(context):
    respx.post(f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/BatchAssignBeds").mock(
        return_value=Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        )
    )


@when("the request is made to assign some beds")
def step_impl(context):
    context.response = context.client.put(**context.request)
