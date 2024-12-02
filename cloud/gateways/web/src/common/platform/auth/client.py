import json

import httpx
from fastapi import HTTPException
from starlette import status

from src.auth.schemas import (
    InternalToken,
    LoginCredential,
    RefreshedInternalToken,
    RefreshToken,
    TechnicalLoginCredential,
)
from src.common.platform.auth.schemas import (
    PlatformChangePasswordPayload,
    PlatformLogout,
)
from src.common.platform.common.http_base import BaseClient
from src.settings import settings


async def get_internal_token(payload: LoginCredential | TechnicalLoginCredential) -> InternalToken:
    url = f"{settings.AUTH_PLATFORM_BASE_URL}/token"
    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
        }
        response = await client.post(
            url,
            headers=headers,
            content=payload.model_dump_json(),
        )
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            detail = json.loads(response.text).get("detail")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        if response.status_code == status.HTTP_403_FORBIDDEN and response.text:
            detail = json.loads(response.text).get("detail")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        response.raise_for_status()

    return InternalToken(**json.loads(response.text))


async def refresh_internal_token(refresh_token: RefreshToken) -> RefreshedInternalToken:
    url = f"{settings.AUTH_PLATFORM_BASE_URL}/token/refresh"
    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
        }
        response = await client.post(
            url,
            headers=headers,
            content=refresh_token.model_dump_json(),
        )
        response.raise_for_status()
    return RefreshedInternalToken.model_validate_json(response.text)


class AuthPlatformClient(BaseClient):
    root_url: str = f"{settings.AUTH_PLATFORM_BASE_URL}"

    async def logout(self, payload: PlatformLogout) -> None:
        url = f"{settings.AUTH_PLATFORM_BASE_URL}/token/logout"
        response = await self.client.post(url, content=payload.model_dump_json())

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            detail = response.json().get("msg")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        if response.status_code == status.HTTP_403_FORBIDDEN:
            detail = json.loads(response.text).get("msg")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        if response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        response.raise_for_status()

    async def change_password(self, payload: PlatformChangePasswordPayload) -> None:
        url = f"{settings.AUTH_PLATFORM_BASE_URL}/auth/change-password"
        response = await self.client.post(url, content=payload.model_dump_json())
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            detail = response.json().get("msg")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        response.raise_for_status()
