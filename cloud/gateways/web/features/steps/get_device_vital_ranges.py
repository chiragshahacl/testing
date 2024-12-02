import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to get vital ranges for a certain device")
def step_impl(context):
    context.device_id = "c205caa0-eadb-4fde-9d9d-09c83f4009ff"
    context.request = {
        "url": f"/web/device/{context.device_id}/range",
    }


@step("the device has several ranges in existence")
def step_impl(context):
    context.expected_response = {
        "resources": [
            {
                "id": "adb72b51-81c1-4397-aab4-be875377875c",
                "code": "10000",
                "upper_limit": 105.67,
                "lower_limit": 50.68,
            },
            {
                "id": "a8ed99ba-526d-4787-826c-f4d6626ce916",
                "code": "10001",
                "upper_limit": 110.67,
                "lower_limit": 70.29,
            },
            {
                "id": "61f9f074-8acb-4828-bc77-a79697996404",
                "code": "10002",
                "upper_limit": 45.67,
                "lower_limit": 5.01,
            },
        ]
    }
    respx.get(
        f"{settings.DEVICE_PLATFORM_BASE_URL}/{context.device_id}/ranges",
        headers=context.request.get("headers"),
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json=context.expected_response,
        )
    )

    context.expected_response_map = {
        item["id"]: item for item in context.expected_response["resources"]
    }


@when("the request is made to get vital ranges")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("the vital ranges are returned")
def step_impl(context):
    resp = context.response.json()
    assert resp
    for _range in resp["resources"]:
        assert _range["id"] in context.expected_response_map
        mapping = context.expected_response_map[_range["id"]]
        assert _range["upper_limit"] == mapping["upper_limit"]
        assert _range["code"] == mapping["code"]
        assert _range["lower_limit"] == mapping["lower_limit"]
