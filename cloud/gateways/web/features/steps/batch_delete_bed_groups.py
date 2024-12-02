import uuid

import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to batch delete a bed group")
def step_impl(context):
    context.bed_group_ids = [str(uuid.uuid4())]
    context.payload = {"group_ids": context.bed_group_ids}

    context.request = {
        "url": "/web/bed-group/batch",
        "json": context.payload,
    }


@step("a request to batch delete bed groups")
def step_impl(context):
    context.bed_group_ids = [str(uuid.uuid4()) for _ in range(3)]
    context.payload = {"group_ids": context.bed_group_ids}

    context.request = {
        "url": "/web/bed-group/batch",
        "json": context.payload,
    }


@step("the bed groups can be deleted")
def step_impl(context):
    respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/BatchDeleteBedGroups",
        json=context.payload,
    ).mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    )


@step("the bed groups can't be deleted")
def step_impl(context):
    respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/BatchDeleteBedGroups",
        json=context.payload,
    ).mock(
        return_value=Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        )
    )


@when("the request is made to batch delete bed groups")
def step_impl(context):
    context.response = context.client.request(
        method="DELETE",
        **context.request,
    )
