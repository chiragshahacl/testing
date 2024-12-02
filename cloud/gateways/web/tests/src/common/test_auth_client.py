import json

import httpx
import pytest
import respx
from httpx import Response

from src.auth.schemas import (
    LoginCredential,
    RefreshToken,
)
from src.common.platform.auth import client
from src.common.platform.auth.schemas import (
    PlatformChangePasswordPayload,
    PlatformLogout,
)
from src.settings import settings


@pytest.mark.asyncio
async def test_get_internal_token_is_secret(respx_mock):
    payload = LoginCredential(username="username", password="password")
    response = {"access": "access1", "refresh": "refresh1"}
    respx_mock.post(f"{settings.AUTH_PLATFORM_BASE_URL}/token").mock(
        return_value=Response(200, text=json.dumps(response))
    )

    result = await client.get_internal_token(payload)

    last_request = respx.calls.last.request
    assert json.loads(last_request.content) == {
        "username": "username",
        "password": "password",
    }
    assert result.access.get_secret_value() == "access1"
    assert result.refresh.get_secret_value() == "refresh1"


@pytest.mark.asyncio
async def test_refresh_internal_token_is_secret(respx_mock):
    payload = RefreshToken(refresh="refresh1")
    response = {"access": "access1"}

    respx_mock.post(f"{settings.AUTH_PLATFORM_BASE_URL}/token/refresh").mock(
        return_value=Response(200, text=json.dumps(response))
    )

    result = await client.refresh_internal_token(payload)

    last_request = respx.calls.last.request
    assert json.loads(last_request.content) == {
        "refresh": "refresh1",
    }
    assert result.access.get_secret_value() == "access1"


@pytest.mark.asyncio
async def test_logout_is_secret(respx_mock):
    payload = PlatformLogout(password="password1")
    respx_mock.post(f"{settings.AUTH_PLATFORM_BASE_URL}/token/logout") % 200
    http_client = httpx.AsyncClient()

    await client.AuthPlatformClient(http_client).logout(payload)

    last_request = respx.calls.last.request
    assert json.loads(last_request.content) == {
        "password": "password1",
    }


@pytest.mark.asyncio
async def test_change_password_is_secret(respx_mock):
    payload = PlatformChangePasswordPayload(
        current_password="password1", new_password="new-password"
    )
    respx_mock.post(f"{settings.AUTH_PLATFORM_BASE_URL}/auth/change-password") % 200
    http_client = httpx.AsyncClient()

    await client.AuthPlatformClient(http_client).change_password(payload)

    last_request = respx.calls.last.request
    assert json.loads(last_request.content) == {
        "current_password": "password1",
        "new_password": "new-password",
    }
