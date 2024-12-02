import json

import respx
from behave import step, when
from httpx import Response
from starlette import status

from common import generate_valid_jwt_token
from src.settings import settings


@step("a valid request to logout")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.request = {
        "url": "/web/auth/token/logout",
        "headers": {"Authorization": context.valid_token},
        "json": {"password": "password_123"},
    }
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/token/logout",
        headers={"Authorization": context.valid_token},
        json={"password": "password_123"},
    ).mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    )


@step("a forbidden request to logout")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.request = {
        "url": "/web/auth/token/logout",
        "headers": {"Authorization": context.valid_token},
        "json": {"password": "password_123"},
    }
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/token/logout",
        headers={"Authorization": context.valid_token},
        json={"password": "password_123"},
    ).mock(
        return_value=Response(
            status_code=status.HTTP_403_FORBIDDEN,
            text=json.dumps({"msg": "403"}),
        )
    )


@step("an invalid request to logout")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.invalid_token = token
    context.request = {
        "url": "/web/auth/token/logout",
        "headers": {"Authorization": context.invalid_token},
        "json": {"password": "password_123"},
    }
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/token/logout",
        headers={"Authorization": context.invalid_token},
        json={"password": "password_123"},
    ).mock(
        return_value=Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        )
    )


@when("the request to logout is made")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the password is invalid")
def step_impl(context):
    context.request["json"] = {"password": "123"}
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/token/logout",
        headers={"Authorization": context.valid_token},
        json={"password": "123"},
    ).mock(
        return_value=Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        )
    )
