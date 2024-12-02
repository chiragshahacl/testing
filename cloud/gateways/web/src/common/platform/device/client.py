from typing import Optional
from uuid import UUID

from src.common.platform.common.http_base import BaseClient
from src.common.platform.device.schemas import (
    PlatformBatchAssignBeds,
    PlatformBatchUnassignBeds,
    PlatformCreateDevice,
    PlatformDevice,
    PlatformDeviceQueryParams,
    PlatformDeviceRangesResources,
    PlatformDeviceResources,
    PlatformUpdateDevice,
)
from src.settings import settings


class DevicePlatformClient(BaseClient):
    root_url: str = f"{settings.DEVICE_PLATFORM_BASE_URL}"

    async def get_device_by_identifier(self, device_identifier: str) -> PlatformDevice:
        response = await self.client.get(url=self.root_url + "/" + device_identifier)
        response.raise_for_status()
        return PlatformDevice.model_validate_json(response.text)

    async def get_devices(
        self, params: Optional[PlatformDeviceQueryParams] = None
    ) -> PlatformDeviceResources:
        if params:
            params = params.model_dump(exclude_none=True)
        response = await self.client.get(url=self.root_url, params=params)
        response.raise_for_status()
        return PlatformDeviceResources.model_validate_json(response.text)

    async def batch_assign_beds(
        self,
        payload: PlatformBatchAssignBeds,
    ):
        response = await self.client.post(
            f"{self.root_url}/BatchAssignLocation", content=payload.model_dump_json()
        )
        response.raise_for_status()

    async def batch_unassign_beds(
        self,
        payload: PlatformBatchUnassignBeds,
    ):
        response = await self.client.post(
            f"{self.root_url}/BatchUnassignLocation", content=payload.model_dump_json()
        )
        response.raise_for_status()

    async def update_device(
        self,
        payload: PlatformUpdateDevice,
    ) -> None:
        response = await self.client.post(
            f"{self.root_url}/UpdateDevice", content=payload.model_dump_json()
        )
        response.raise_for_status()

    async def create_device(
        self,
        payload: PlatformCreateDevice,
    ) -> None:
        response = await self.client.post(
            f"{self.root_url}/CreateDevice", content=payload.model_dump_json()
        )
        response.raise_for_status()

    async def get_device_vital_ranges(
        self,
        device_id: UUID,
    ) -> PlatformDeviceRangesResources:
        response = await self.client.get(f"{self.root_url}/{device_id}/ranges")
        return PlatformDeviceRangesResources.model_validate_json(response.text)
