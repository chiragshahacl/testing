import httpx
import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to batch create some beds")
def step_impl(context):
    context.names = ["bed1", "bed2", "bed3"]
    context.payload = [{"name": "bed1"}, {"name": "bed2"}, {"name": "bed3"}]
    context.request = {
        "url": "/web/bed/batch",
        "json": {"resources": context.payload},
    }


@step("the beds can be made")
def step_impl(context):
    respx.post(f"{settings.PATIENT_PLATFORM_BASE_URL}/bed/BatchCreateBeds").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "resources": [
                    {
                        "id": "d6797a1a-1900-43d7-912f-d2692fd39399",
                        "name": "bed1",
                        "patient": None,
                    },
                    {
                        "id": "ff01a8f8-8294-4307-8c8c-578ba1e9a17a",
                        "name": "bed2",
                        "patient": None,
                    },
                    {
                        "id": "e044bbb5-0866-4997-862b-8ef9e6432a84",
                        "name": "bed3",
                        "patient": None,
                    },
                ]
            },
        )
    )
    context.req_body = httpx.post(f"{settings.PATIENT_PLATFORM_BASE_URL}/bed/BatchCreateBeds")


@step("the beds cant be made")
def step_impl(context):
    respx.post(f"{settings.PATIENT_PLATFORM_BASE_URL}/bed/BatchCreateBeds").mock(
        return_value=Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        )
    )


@when("the request is made to batch create some beds")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the list of beds is returned")
def step_impl(context):
    beds = {}
    req = context.req_body.json()
    for bed in req["resources"]:
        beds[bed["id"]] = bed["name"]

    resp = context.response.json()
    for item in resp["resources"]:
        assert item["name"] in context.names
        assert beds[item["id"]] == item["name"]
