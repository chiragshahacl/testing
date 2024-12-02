import random
import uuid
from datetime import datetime

import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("devices are found")
def step_impl(context):
    context.mocked_response = {
        "resources": [
            {
                "id": str(uuid.uuid4()),
                "primary_identifier": f"identifier {i}",
                "name": f"device name {i}",
                "location": str(uuid.uuid4()),
                "gateway_id": str(uuid.uuid4()),
                "device_code": f"device-code-{i}",
                "vital_ranges": [
                    {
                        "id": str(uuid.uuid4()),
                        "code": f"code-{j}",
                        "upper_limit": 10,
                        "lower_limit": 1,
                        "alert_condition_enabled": True,
                    }
                    for j in range(5)
                ],
                "alerts": [
                    {
                        "id": str(uuid.uuid4()),
                        "code": f"code-{m}",
                        "priority": random.choice(["LO", "ME", "HI"]),
                        "created_at": datetime.utcnow().isoformat(),
                    }
                    for m in range(3)
                ],
                "audio_pause_enabled": False,
                "audio_enabled": True,
            }
            for i in range(5)
        ]
    }
    for obj in context.mocked_response["resources"]:
        obj["model_number"] = obj.pop("device_code")


@step("bed group has beds")
def step_impl(context):
    context.mocked_bed_group = {
        "resources": [
            {
                "id": str(uuid.uuid4()),
                "name": f"Bed {i}",
                "patient": None,
            }
            for i in range(2)
        ]
    }
    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/0ee875b1-7722-4fe4-b26e-889fa5b257ec/beds",
        headers=context.request.get("headers"),
    ).mock(
        return_value=Response(
            status_code=context.expected_code,
            json=context.mocked_bed_group,
        )
    )


@step("a request to get a device list")
def step_impl(context):
    context.request = {
        "url": "/web/device",
    }
    context.expected_code = status.HTTP_200_OK


@when("the request is made to get a device list")
def step_impl(context):
    # TODO: improve this test
    if params := context.request.get("params"):
        mapped_params = {
            "gateway": params.get("gatewayId"),
            "location_id": params.get("bedId"),
            "is_gateway": params.get("isGateway"),
            "device_code": params.get("deviceCode"),
        }
        if params.get("bedGroup"):
            mapped_params["location_id"] = [
                bed["id"] for bed in context.mocked_bed_group["resources"]
            ]
        params = {k: v for k, v in mapped_params.items() if v is not None}

    respx.get(
        f"{settings.DEVICE_PLATFORM_BASE_URL}",
        headers=context.request.get("headers"),
        params=params,
    ).mock(
        return_value=Response(
            status_code=context.expected_code,
            json=context.mocked_response,
        )
    )

    context.response = context.client.get(**context.request)


@step("a device list is returned")
def step_impl(context):
    devices = context.response.json()["resources"]

    for device in devices:
        assert "id" in device
        assert "primary_identifier" in device
        assert "name" in device
        assert "location_id" in device
        assert "gateway_id" in device
        assert "device_code" in device
        assert "alerts" in device
        for alert in device["alerts"]:
            assert "id" in alert
            assert "code" in alert
            assert "priority" in alert
            assert "createdAt" in alert

        assert "vital_ranges" in device
        for vr in device["vital_ranges"]:
            assert "id" in vr
            assert "upper_limit" in vr
            assert "lower_limit" in vr
            assert "code" in vr
        assert "config" in device
        assert "audio_enabled" in device["config"]
        assert "audio_pause_enabled" in device["config"]
        assert device["config"]["audio_enabled"] is True
        assert device["config"]["audio_pause_enabled"] is False


@step("filtering by `{query_param}` `{value}`")
def step_impl(context, query_param, value):
    context.request["params"] = {query_param: value, "isGateway": False}


@step("filtering by all the params")
def step_impl(context):
    context.request["params"] = {
        "gateway_id": "8adea8ff-320f-48d3-8d3d-0d5e7007994c",
        "bed_id": "e3dd6f29-b7ca-42af-8e4f-f517fdd07fc1",
        "is_gateway": True,
        "device_code": "DCODE",
        "bed_group": "a3dd6f19-b2bd-23ad-a85d-0c5f1112394f",
    }
