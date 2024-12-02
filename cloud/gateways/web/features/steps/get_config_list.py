import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.config.schemas import WebConfigResources
from src.settings import settings


@step("configs are found")
def step_impl(context):
    context.config_key = "MLLP_PORT"
    context.config_value = "2024"
    context.expected_response = {
        "resources": [
            {
                "key": context.config_key,
                "value": context.config_value,
            }
        ]
    }


@step("configs not found")
def step_impl(context):
    context.expected_response = {"resources": []}


@step("a request to get the config list")
def step_impl(context):
    context.request = {
        "url": "/web/config",
    }
    context.expected_code = status.HTTP_200_OK


@when("the request is made to get the config list")
def step_impl(context):
    respx.get(
        f"{settings.AUTH_PLATFORM_BASE_URL}/configuration/",
        headers=context.request.get("headers"),
    ).mock(
        return_value=Response(
            status_code=context.expected_code,
            json=context.expected_response,
        )
    )
    context.response = context.client.get(**context.request)


@step("a config list is returned")
def step_impl(context):
    config_response = WebConfigResources(**context.response.json())
    expected_response = WebConfigResources(**context.expected_response)
    assert config_response == expected_response


@step("an empty config list is returned")
def step_impl(context):
    config_response = WebConfigResources(**context.response.json())
    assert not config_response.resources
