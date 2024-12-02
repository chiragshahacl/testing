import respx
from behave import step
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to create or update a device (create)")
def step_impl(context):
    context.payload = {
        "id": "531ccdc2-e135-4b94-883c-8fb859ef50e8",
        "name": "device0",
        "primary_identifier": "PID-000",
        "gateway_id": "7d34b272-badf-404a-8d94-46faba9365c6",
        "device_code": "1234-code-1234",
    }
    context.request = {
        "url": "/web/device",
        "json": context.payload,
    }


@step("a request to create or update a device (update)")
def step_impl(context):
    context.payload = {
        "id": "bccf36c0-3624-4637-a4fc-f15e8b65e24b",
        "name": "device0",
        "primary_identifier": "PID-000",
        "gateway_id": "7d34b272-badf-404a-8d94-46faba9365c6",
        "device_code": "device-code-000",
    }
    context.request = {
        "url": "/web/device",
        "json": context.payload,
    }


@step("several devices exist")
def step_impl(context):
    respx.get(f"{settings.DEVICE_PLATFORM_BASE_URL}").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "resources": [
                    {
                        "id": "bccf36c0-3624-4637-a4fc-f15e8b65e24b",
                        "name": "device1",
                        "primary_identifier": "PID-001",
                        "gateway_id": "72a2f0ac-9268-4380-84b4-35a9ac6e508f",
                        "location_id": "d92ec427-9dd6-458b-91b2-ef2f66a7f9d1",
                        "model_number": "device-code-001",
                        "audio_pause_enabled": False,
                        "audio_enabled": True,
                    },
                    {
                        "id": "ff01a8f8-8294-4307-8c8c-578ba1e9a17a",
                        "name": "device2",
                        "primary_identifier": "PID-002",
                        "gateway_id": "ae29de9a-5892-4be9-bf9a-2047c3ba9c64",
                        "location_id": "a36e256e-4be5-481a-bbf2-b430635e60fe",
                        "model_number": "device-code-002",
                        "audio_pause_enabled": False,
                        "audio_enabled": True,
                    },
                    {
                        "id": "e044bbb5-0866-4997-862b-8ef9e6432a84",
                        "name": "device3",
                        "primary_identifier": "PID-003",
                        "gateway_id": "beba62be-dfbd-43b1-9d5e-a254e97938d8",
                        "location_id": "7f457c8d-6409-45c9-b22b-98c54517244e",
                        "model_number": "device-code-003",
                        "audio_pause_enabled": False,
                        "audio_enabled": True,
                    },
                ]
            },
        )
    )


@step("the device can be created")
def step_impl(context):
    respx.post(f"{settings.DEVICE_PLATFORM_BASE_URL}/CreateDevice").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "id": "bccf36c0-3624-4637-a4fc-f15e8b65e24b",
                "name": "device0",
                "primary_identifier": "PID-000",
                "gateway_id": "7d34b272-badf-404a-8d94-46faba9365c6",
                "location_id": "028f181e-5bf8-4d84-929f-b4343c1f585d",
                "model_number": "1234-code-1234",
            },
        )
    )


@step("the device can be updated")
def step_impl(context):
    respx.post(f"{settings.DEVICE_PLATFORM_BASE_URL}/UpdateDevice").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "id": "bccf36c0-3624-4637-a4fc-f15e8b65e24b",
                "name": "device0",
                "primary_identifier": "PID-000",
                "gateway_id": "7d34b272-badf-404a-8d94-46faba9365c6",
                "location_id": "028f181e-5bf8-4d84-929f-b4343c1f585d",
                "model_number": "device-code-000",
            },
        )
    )


@step("the request is made to create or update a device")
def step_impl(context):
    context.response = context.client.put(**context.request)
