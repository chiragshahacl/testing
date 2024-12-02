from src.common.platform.common.http_base import BaseClient
from src.common.platform.config.schemas import PlatformConfigResources, PlatformUpdateConfigBatch
from src.settings import settings


class ConfigPlatformClient(BaseClient):
    root_url: str = f"{settings.AUTH_PLATFORM_BASE_URL}"

    async def get_configs(self) -> PlatformConfigResources:
        response = await self.client.get(f"{self.root_url}/configuration/")
        response.raise_for_status()

        return PlatformConfigResources.model_validate_json(response.text)

    async def create_config_batch(self, payload: PlatformUpdateConfigBatch):
        response = await self.client.post(
            f"{self.root_url}/configuration/",
            content=payload.model_dump_json(),
        )
        response.raise_for_status()
