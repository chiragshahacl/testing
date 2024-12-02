import httpx
from fastapi import Depends

from src.common.dependencies import PlatformHttpClient
from src.common.platform.config.client import ConfigPlatformClient
from src.config import schemas as web_config_schemas


class ConfigService:
    def __init__(self, http_client: httpx.AsyncClient = Depends(PlatformHttpClient())):
        self.http_client = http_client
        self.config_client = ConfigPlatformClient(self.http_client)

    async def get_configs(self) -> web_config_schemas.WebConfigResources:
        platform_config_resources = await self.config_client.get_configs()
        return web_config_schemas.WebConfigResources.from_platform(platform_config_resources)

    async def create_or_update_configs(self, payload: web_config_schemas.WebUpdateOrCreateConfig):
        configs = web_config_schemas.WebUpdateOrCreateConfig.to_platform(payload)
        await self.config_client.create_config_batch(configs)
