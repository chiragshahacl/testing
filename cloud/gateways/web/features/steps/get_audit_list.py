import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to get list of audit events")
def step_impl(context):
    context.entity_id = "3af220a8-4132-4d66-9097-c6daaced7442"
    context.request = {"url": f"/web/audit/{context.entity_id}"}
    context.expected_response = {
        "resources": [
            {
                "entity_id": context.entity_id,
                "event_name": "Create Device",
                "timestamp": "2022-02-08 00:00:00",
                "data": {},
            },
            {
                "entity_id": context.entity_id,
                "event_name": "Delete Device",
                "timestamp": "2021-02-08 00:00:00",
                "data": {},
            },
            {
                "entity_id": context.entity_id,
                "event_name": "Update Device",
                "timestamp": "2020-02-08 00:00:00",
                "data": {},
            },
        ],
        "total": 3,
    }


@step("several audit events exist")
def step_impl(context):
    respx.get(
        f"{settings.AUDIT_PLATFORM_BASE_URL}/{context.entity_id}",
        headers=context.request.get("headers"),
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json=context.expected_response,
        )
    )


@step("no audit events exist")
def step_impl(context):
    respx.get(
        f"{settings.AUDIT_PLATFORM_BASE_URL}/{context.entity_id}",
        headers=context.request.get("headers"),
    ).mock(
        return_value=Response(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    )


@when("the request is made to get list of audit events")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("the list of audit events is returned")
def step_impl(context):
    resp = context.response.json()
    assert resp["resources"]
    assert len(resp["resources"]) == 3
    for event in resp["resources"]:
        assert "entity_id" in event
        assert "event_name" in event
        assert "data" in event
        assert "timestamp" in event
