import httpx
import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to batch create some bed groups")
def step_impl(context):
    context.names = ["bed1", "bed2", "bed3"]
    context.payload = [
        {"name": "bed1", "description": "desc1"},
        {"name": "bed2", "description": "desc2"},
        {"name": "bed3", "description": "desc2"},
    ]
    context.request = {
        "url": "/web/bed-group/batch",
        "json": {"resources": context.payload},
    }


@step("the bed groups can be made")
def step_impl(context):
    respx.post(f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/BatchCreateBedGroups").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "resources": [
                    {
                        "id": "d6797a1a-1900-43d7-912f-d2692fd39399",
                        "name": "bed1",
                        "description": "desc1",
                        "beds": [],
                    },
                    {
                        "id": "ff01a8f8-8294-4307-8c8c-578ba1e9a17a",
                        "name": "bed2",
                        "description": "desc2",
                        "beds": [],
                    },
                    {
                        "id": "e044bbb5-0866-4997-862b-8ef9e6432a84",
                        "name": "bed3",
                        "description": "desc3",
                        "beds": [],
                    },
                ]
            },
        )
    )
    context.req_body = httpx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/BatchCreateBedGroups"
    )


@step("the bed groups cant be made")
def step_impl(context):
    respx.post(f"{settings.PATIENT_PLATFORM_BASE_URL}/bed-group/BatchCreateBedGroups").mock(
        return_value=Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        )
    )


@when("the request is made to batch create some bed groups")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the list of bed groups is returned")
def step_impl(context):
    bed_groups = {}
    req = context.req_body.json()
    for bed_group in req["resources"]:
        bed_groups[bed_group["id"]] = (bed_group["name"], bed_group["description"])

    resp = context.response.json()
    for item in resp["resources"]:
        assert item["name"] in context.names
        assert bed_groups[item["id"]][0] == item["name"]
        assert bed_groups[item["id"]][1] == item["description"]
