import hashlib
import json
import pickle
import uuid

import respx
from behave import step
from httpx import Response
from starlette import status

from src.event_sourcing.schemas import CommandResponseEventState
from src.settings import settings


@step("device can execute command")
def step_impl(context):
    response = CommandResponseEventState(request_id=uuid.uuid4(), success=True, errors=None)
    context.mock_check_for_response.return_value = response


@step("device executes command with error")
def step_impl(context):
    response = CommandResponseEventState(
        request_id=uuid.uuid4(), success=False, errors=["Failed to execute command."]
    )
    context.mock_check_for_response.return_value = response


@step("device cannot execute command")
def step_impl(context):
    context.mock_check_for_response.return_value = None


@step("device exists as a patient monitor")
def step_impl(context):
    context.response = {
        "id": str(uuid.uuid4()),
        "primary_identifier": "a7bfb1c7-5b4f-4e3d-a6b1-785ddaeed41b",
        "name": "device name",
        "location_id": str(uuid.uuid4()),
        "gateway_id": None,
        "device_code": "device-code",
        "model_number": "device-code",
        "vital_ranges": [],
        "alerts": [],
        "audio_pause_enabled": False,
        "audio_enabled": True,
    }
    respx.get(f"{settings.DEVICE_PLATFORM_BASE_URL}/a7bfb1c7-5b4f-4e3d-a6b1-785ddaeed41b").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json=context.response,
        )
    )


@step("device is connected")
def step_impl(context):
    context.cache.set(
        "sdc/device/primaryIdentifier/a7bfb1c7-5b4f-4e3d-a6b1-785ddaeed41b",
        pickle.dumps({"connected": True}),
    )


@step("device is executing another command")
def step_impl(context):
    request_hash = hashlib.sha1(f"{context.request['url']}:".encode()).hexdigest()
    context.cache.set(
        f"web:web-command-lock-a7bfb1c7-5b4f-4e3d-a6b1-785ddaeed41b:{request_hash}",
        pickle.dumps({"locked": True}),
    )


@step("other device is executing another command")
def step_impl(context):
    request_hash = hashlib.sha1(f"{context.request['url']}:".encode()).hexdigest()
    context.cache.set(
        f"web:web-command-lock-identifier1:{request_hash}",
        pickle.dumps({"locked": True}),
    )


@step("device exists as a sensor")
def step_impl(context):
    respx.get(f"{settings.DEVICE_PLATFORM_BASE_URL}/a7bfb1c7-5b4f-4e3d-a6b1-785ddaeed41b").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "id": str(uuid.uuid4()),
                "primary_identifier": "a7bfb1c7-5b4f-4e3d-a6b1-785ddaeed41b",
                "name": "device name",
                "location_id": str(uuid.uuid4()),
                "gateway_id": str(uuid.uuid4()),
                "device_code": "device-code",
                "model_number": "device-code",
                "vital_ranges": [],
                "alerts": [],
                "audio_pause_enabled": False,
                "audio_enabled": True,
            },
        )
    )


@step("a request to send application valid command")
def step_impl(context):
    context.payload = {
        "command_name": "ALARM_VALIDATION_OFF",
        "pm_identifier": "a7bfb1c7-5b4f-4e3d-a6b1-785ddaeed41b",
        "params": {},
    }
    context.request = {
        "url": "/web/device/command",
        "json": context.payload,
    }


@step("a request to send application invalid command")
def step_impl(context):
    context.payload = {
        "command_name": "INVALID_COMMAND",
        "pm_identifier": "a7bfb1c7-5b4f-4e3d-a6b1-785ddaeed41b",
        "params": {},
    }
    context.request = {
        "url": "/web/device/command",
        "json": context.payload,
    }


@step("the request is made to send application command")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the user is told the device is not a patient monitor")
def step_impl(context):
    response_content = context.response.content.decode("utf-8")
    response_json = json.loads(response_content)
    assert response_json["detail"][0]["msg"] == "Device is not a patient monitor."


@step("the user is told the device is already executing another command")
def step_impl(context):
    response_content = context.response.content.decode("utf-8")
    response_json = json.loads(response_content)
    assert response_json["detail"][0]["msg"] == "Device is already executing another command."


@step("the user is told the device is not connected")
def step_impl(context):
    response_content = context.response.content.decode("utf-8")
    response_json = json.loads(response_content)
    assert response_json["detail"][0]["msg"] == "Device is not connected."


@step("the user is told connection failed")
def step_impl(context):
    response_content = context.response.content.decode("utf-8")
    response_json = json.loads(response_content)
    assert response_json["detail"][0]["msg"] == "Could not connect with device."


@step("the user is told command execution failed")
def step_impl(context):
    response_content = context.response.content.decode("utf-8")
    response_json = json.loads(response_content)
    assert response_json["detail"][0]["type"] == "execution_error.failed"
