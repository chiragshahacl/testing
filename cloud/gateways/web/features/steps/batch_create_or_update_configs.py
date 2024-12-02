import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to batch create or update configs with `{field_name}` `{field_value}`")
def step_impl(context, field_name, field_value):
    if field_name == "MLLP_PORT":
        context.payload = {
            "password": "password",
            "config": {
                "MLLP_HOST": "198.51.100.42",
                "MLLP_PORT": field_value,
                "MLLP_EXPORT_INTERVAL_MINUTES": 1,
            },
        }
    elif field_name == "MLLP_EXPORT_INTERVAL_MINUTES":
        context.payload = {
            "password": "password",
            "config": {
                "MLLP_HOST": "198.51.100.42",
                "MLLP_PORT": 0,
                "MLLP_EXPORT_INTERVAL_MINUTES": field_value,
            },
        }
    else:
        context.payload = {
            "password": "password",
            "config": {
                "MLLP_HOST": field_value,
                "MLLP_PORT": 0,
                "MLLP_EXPORT_INTERVAL_MINUTES": 1,
            },
        }

    context.request = {
        "url": "/web/config",
        "json": context.payload,
    }


@step("a request to batch create or update configs")
def step_impl(context):
    context.payload = {
        "password": "password",
        "config": {
            "MLLP_HOST": "198.51.100.42",
            "MLLP_PORT": 0,
            "MLLP_EXPORT_INTERVAL_MINUTES": 1,
        },
    }

    context.request = {
        "url": "/web/config",
        "json": context.payload,
    }


@when("the request is made to batch create or update some configs")
def step_impl(context):
    context.response = context.client.put(**context.request)


@step("the configs can be created or updated")
def step_impl(context):
    context.batch_update_response = respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/configuration/",
        json={
            "configs": [
                {"key": "MLLP_HOST", "value": "198.51.100.42"},
                {"key": "MLLP_PORT", "value": "0"},
                {"key": "MLLP_EXPORT_INTERVAL_MINUTES", "value": "1"},
            ]
        },
    ).mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    )


@step("payload contains valid password")
def step_impl(context):
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/token",
        headers={"Content-Type": "application/json"},
        json={
            "username": settings.DEFAULT_TECHNICAL_USER_USERNAME,
            "password": context.payload["password"],
        },
    ).mock(
        return_value=Response(
            json={
                "access": "expected-access-token",
                "refresh": "expected-refresh-token",
            },
            status_code=status.HTTP_200_OK,
        )
    )


@step("payload contains invalid password")
def step_impl(context):
    respx.post(
        f"{settings.AUTH_PLATFORM_BASE_URL}/token",
        headers={"Content-Type": "application/json"},
        json={
            "username": settings.DEFAULT_TECHNICAL_USER_USERNAME,
            "password": context.payload["password"],
        },
    ).mock(
        return_value=Response(
            json={},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    )
