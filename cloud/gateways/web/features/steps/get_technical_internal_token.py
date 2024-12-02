import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a valid request to obtain a technical internal token")
def step_impl(context):
    context.request = {
        "url": "/web/auth/technical/token",
        "headers": {"Content-Type": "application/json"},
        "json": {"password": "validPassword1!"},
    }

    context.expected_response = {
        "access": "expected-access-token",
        "refresh": "expected-refresh-token",
    }

    context.expected_code = status.HTTP_200_OK


@when("the request to get a technical internal token is made")
def step_impl(context):
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/token",
        headers={"Content-Type": "application/json"},
        json={
            "username": settings.DEFAULT_TECHNICAL_USER_USERNAME,
            "password": context.request.get("json").get("password"),
        },
    ).mock(
        return_value=Response(
            json=context.expected_response,
            status_code=context.expected_code,
        )
    )
    context.response = context.client.post(**context.request)
