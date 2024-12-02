import httpx
from fastapi import Depends

from src.bed import schemas as web_bed_schemas
from src.common.dependencies import PlatformHttpClient
from src.common.platform.device.client import DevicePlatformClient
from src.common.platform.device.schemas import (
    PlatformBatchUnassignBeds,
    PlatformDeviceQueryParams,
)
from src.common.platform.patient.client import PatientPlatformClient


class BedService:
    def __init__(self, http_client: httpx.AsyncClient = Depends(PlatformHttpClient())):
        self.http_client = http_client
        self.patient_client = PatientPlatformClient(self.http_client)
        self.device_client = DevicePlatformClient(self.http_client)

    async def get_beds(self) -> web_bed_schemas.WebBedResources:
        platform_bed_resources = await self.patient_client.get_beds()
        return web_bed_schemas.WebBedResources.from_platform(platform_bed_resources)

    async def batch_create_beds(
        self, payload: web_bed_schemas.WebBatchCreateBeds
    ) -> web_bed_schemas.WebBedResources:
        beds = await self.patient_client.create_bed_batch(payload.to_platform())
        return web_bed_schemas.WebBedResources.from_platform(beds)

    async def create_or_update_beds(self, payload: web_bed_schemas.WebBatchCreateOrUpdateBeds):
        all_beds = await self.patient_client.get_beds()
        bed_map = {bed.id: bed for bed in all_beds.resources}
        beds_to_create = []
        beds_to_update = []
        for bed in payload.resources:
            if not bed.id or bed.id not in bed_map:
                beds_to_create.append(bed)
            else:
                current_state = bed_map[bed.id]
                if bed.name != current_state.name:
                    beds_to_update.append(bed)
        if beds_to_update:
            await self.patient_client.update_bed_batch(
                web_bed_schemas.WebBatchCreateOrUpdateBeds.to_platform_batch_update(beds_to_update)
            )
        if beds_to_create:
            await self.patient_client.create_bed_batch(
                web_bed_schemas.WebBatchCreateOrUpdateBeds.to_platform_batch_create(beds_to_create)
            )

    async def batch_delete_beds(self, payload: web_bed_schemas.WebBatchDeleteBeds) -> None:
        device_qp = PlatformDeviceQueryParams.model_construct(is_gateway=True)
        devices = await self.device_client.get_devices(device_qp)
        device_id_set = set()
        for device in devices.resources:
            if device.location_id in payload.bed_ids:
                device_id_set.add(device.id)

        unassign_payload = PlatformBatchUnassignBeds.model_construct(device_ids=list(device_id_set))

        await self.device_client.batch_unassign_beds(unassign_payload)
        await self.patient_client.delete_bed_batch(payload.to_platform())
