import httpx
from fastapi import Depends

from src.auth.schemas import WebChangePasswordPayload
from src.common.dependencies import PlatformHttpClient
from src.common.platform.auth.client import AuthPlatformClient


class PlatformAuthenticationService:
    def __init__(self, http_client: httpx.AsyncClient = Depends(PlatformHttpClient())):
        self.http_client = http_client
        self.auth_client = AuthPlatformClient(self.http_client)

    async def change_password(self, payload: WebChangePasswordPayload) -> None:
        await self.auth_client.change_password(payload.to_platform())
