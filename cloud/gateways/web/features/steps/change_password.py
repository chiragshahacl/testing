import httpx
import respx
from behave import step, when
from starlette import status

from src.settings import settings


@step("a valid request to change password")
def step_impl(context):
    context.new_password = "new-password"
    context.old_password = "old-password"
    context.request = {
        "url": "/web/auth/change-password",
        "json": {"new": context.new_password, "current": context.old_password},
    }


@step("the provided passwords are correct")
def step_impl(context):
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/auth/change-password",
        json={
            "new_password": context.new_password,
            "current_password": context.old_password,
        },
    ).mock(httpx.Response(status_code=status.HTTP_204_NO_CONTENT))


@step("the provided passwords are not correct")
def step_impl(context):
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/auth/change-password",
        json={
            "new_password": context.new_password,
            "current_password": context.old_password,
        },
    ).mock(
        httpx.Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            json={
                "details": [
                    {
                        "loc": ["string"],
                        "msg": "Account locked.",
                        "type": "string",
                        "ctx": {},
                    }
                ]
            },
        )
    )


@when("the request to change password is made")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the field `{field_name}` is not provided")
def step_impl(context, field_name):
    context.request["json"].pop(field_name, None)
