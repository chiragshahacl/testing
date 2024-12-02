import respx
from behave import step, when
from httpx import Response

from src.settings import settings


@step("a request to refresh an access token")
def step_impl(context):
    context.request = {
        "url": "/web/auth/token/refresh",
        "headers": {"Content-Type": "application/json"},
        "json": {"refresh": "valid-refresh-token"},
    }
    context.expected_token = {
        "access": "new-access-token",
    }
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/token/refresh",
        headers={"Content-Type": "application/json"},
        json={"refresh": "valid-refresh-token"},
    ).mock(
        return_value=Response(
            json=context.expected_token,
            status_code=200,
        )
    )


@step("an invalid request to refresh an access token")
def step_impl(context):
    context.request = {
        "url": "/web/auth/token/refresh",
        "headers": {"Content-Type": "application/json"},
        "json": {"refresh": "invalid-refresh-token"},
    }
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/token/refresh",
        headers={"Content-Type": "application/json"},
        json={"refresh": "invalid-refresh-token"},
    ).mock(
        return_value=Response(
            status_code=401,
        )
    )


@when("the request to get an access token is made")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the refreshed token is included in the response")
def step_impl(context):
    assert context.response.json() == {
        "access": "new-access-token",
    }
