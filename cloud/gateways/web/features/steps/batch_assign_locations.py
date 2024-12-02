import uuid

import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to batch assign location to a device")
def step_impl(context):
    context.bed_id = str(uuid.uuid4())
    context.device_id = str(uuid.uuid4())
    context.payload = [{"bed_id": context.bed_id, "device_id": context.device_id}]

    context.request = {
        "url": "/web/device/bed/batch",
        "json": {"associations": context.payload},
    }


@step("the device can be assigned")
def step_impl(context):
    respx.post(f"{settings.DEVICE_PLATFORM_BASE_URL}/BatchUnassignLocation").mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    )
    respx.post(f"{settings.DEVICE_PLATFORM_BASE_URL}/BatchAssignLocation").mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
            json={"associations": context.payload},
        )
    )


@step("the device can be unassigned")
def step_impl(context):
    respx.post(f"{settings.DEVICE_PLATFORM_BASE_URL}/BatchUnassignLocation").mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
            json={"device_ids": [context.payload[0]["device_id"]]},
        )
    )


@when("the request is made to assign some locations")
def step_impl(context):
    context.response = context.client.put(**context.request)


@step("a request to batch assign multiple locations to devices")
def step_impl(context):
    context.payload = [
        {"bed_id": str(uuid.uuid4()), "device_id": str(uuid.uuid4())} for _ in range(5)
    ]

    context.request = {
        "url": "/web/device/bed/batch",
        "json": {"associations": context.payload},
    }


@step("one of the devices is being unassigned from a bed")
def step_impl(context):
    context.payload.append({"bed_id": None, "device_id": str(uuid.uuid4())})
    print(context.payload)
    context.request = {
        "url": "/web/device/bed/batch",
        "json": {"associations": context.payload},
    }


@step("the location cant be assigned")
def step_impl(context):
    respx.post(f"{settings.DEVICE_PLATFORM_BASE_URL}/BatchAssignLocation").mock(
        return_value=Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        )
    )
    respx.post(f"{settings.DEVICE_PLATFORM_BASE_URL}/BatchAssignLocation").mock(
        return_value=Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        )
    )
