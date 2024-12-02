import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a valid request to obtain an internal token")
def step_impl(context):
    context.request = {
        "url": "/web/auth/token",
        "headers": {"Content-Type": "application/json"},
        "json": {"password": "validPassword1!"},
    }

    context.expected_response = {
        "access": "expected-access-token",
        "refresh": "expected-refresh-token",
    }

    context.expected_code = status.HTTP_200_OK


@when("the request to get an internal token is made")
def step_impl(context):
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/token",
        headers={"Content-Type": "application/json"},
        json={
            "username": settings.DEFAULT_ADMIN_USERNAME,
            "password": context.request.get("json").get("password"),
        },
    ).mock(
        return_value=Response(
            json=context.expected_response,
            status_code=context.expected_code,
        )
    )
    context.response = context.client.post(**context.request)
    print(context.response.status_code)


@step("the token is included in the response")
def step_impl(context):
    assert context.response.json() == {
        "access": "expected-access-token",
        "refresh": "expected-refresh-token",
    }


@step("the password is empty")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.request["json"] = {"password": ""}


@step("the password is incorrect")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.request["json"] = {"password": "invalidPassword1!"}

    context.expected_response = {}

    context.expected_code = status.HTTP_401_UNAUTHORIZED


@step("the request is a bad request")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.request["json"] = {"password": "123"}

    context.expected_response = {}

    context.expected_code = status.HTTP_400_BAD_REQUEST


@step("the password field contains only whitespace characters")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.request["json"] = {"password": "            "}

    context.expected_response = {}

    context.expected_code = status.HTTP_422_UNPROCESSABLE_ENTITY


@step("the account is locked")
def step_impl(context):
    context.expected_response = {"detail": "Account locked."}
    context.expected_code = status.HTTP_403_FORBIDDEN
