import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to batch delete beds")
def step_impl(context):
    context.bed_ids = [
        "27949fec-5f0d-428c-b854-42208d8ec8b5",
        "b11f8afe-126e-484b-aed6-c3c5671ec4c3",
    ]
    context.payload = {"bed_ids": context.bed_ids}

    context.request = {
        "url": "/web/bed/batch",
        "json": context.payload,
    }


@step("a request to batch delete a bed")
def step_impl(context):
    context.bed_ids = ["27949fec-5f0d-428c-b854-42208d8ec8b5"]
    context.payload = {"bed_ids": context.bed_ids}

    context.request = {
        "url": "/web/bed/batch",
        "json": context.payload,
    }


@step("the beds can be deleted")
def step_impl(context):
    respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed/BatchDeleteBeds",
        json=context.payload,
    ).mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    )


@step("several devices exist for batch delete beds")
def step_impl(context):
    respx.get(
        f"{settings.DEVICE_PLATFORM_BASE_URL}?is_gateway=true",
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "resources": [
                    {
                        "id": "55b9dda5-1cc9-4573-939f-e901c045dfd8",
                        "primary_identifier": "PID1",
                        "name": "Device1",
                        "location_id": "27949fec-5f0d-428c-b854-42208d8ec8b5",
                        "model_number": "device-1",
                        "audio_pause_enabled": False,
                        "audio_enabled": True,
                    },
                    {
                        "id": "3a4b8c36-8514-426c-a8e2-06556454780a",
                        "primary_identifier": "PID2",
                        "name": "Device2",
                        "location_id": "b11f8afe-126e-484b-aed6-c3c5671ec4c3",
                        "model_number": "device-2",
                        "audio_pause_enabled": False,
                        "audio_enabled": True,
                    },
                ]
            },
        )
    )


@step("the device can be unassigned when deleting a bed")
def step_impl(context):
    respx.post(
        f"{settings.DEVICE_PLATFORM_BASE_URL}/BatchUnassignLocation",
        json={"device_ids": ["55b9dda5-1cc9-4573-939f-e901c045dfd8"]},
    ).mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    )


@step("the devices can be unassigned")
def step_impl(context):
    res = respx.post(
        f"{settings.DEVICE_PLATFORM_BASE_URL}/BatchUnassignLocation",
        json={
            "device_ids": [
                "55b9dda5-1cc9-4573-939f-e901c045dfd8",
                "3a4b8c36-8514-426c-a8e2-06556454780a",
            ]
        },
    ).mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    )
    print(res)


@step("the beds can't be deleted")
def step_impl(context):
    respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed/BatchDeleteBeds",
        json=context.payload,
    ).mock(
        return_value=Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        )
    )


@when("the request is made to batch delete beds")
def step_impl(context):
    context.response = context.client.request(
        method="DELETE",
        **context.request,
    )
