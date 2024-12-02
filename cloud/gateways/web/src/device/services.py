from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import Depends
from fastapi.requests import Request

from cache import RedisCache, add_lock, get_cache_key, remove_lock
from src.common.dependencies import PlatformHttpClient
from src.common.exceptions import BaseValidationException
from src.common.platform.device.client import DevicePlatformClient
from src.common.platform.device.schemas import (
    PlatformBatchAssignBeds,
    PlatformBatchUnassignBeds,
    PlatformDevice,
)
from src.common.platform.patient.client import PatientPlatformClient
from src.common.schemas import base as common_schemas
from src.device import schemas
from src.device.command_organizer import (
    CommandOrganizer,
    wait_for_device_response,
)
from src.event_sourcing.events import CommandExecutionRequestEvent
from src.event_sourcing.stream import CommandExecutionEventStream


class NotPatientMonitor(BaseValidationException):
    def __init__(self) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body", "id"],
            msg="Device is not a patient monitor.",
            type="value_error.invalid_device_type",
        )


class DeviceConnectionError(BaseValidationException):
    def __init__(self) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body", "id"],
            msg="Device is not connected.",
            type="connection_error.not_connected",
        )


class CommandExecutionError(BaseValidationException):
    def __init__(self, messages: List[str]) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body", "command_name"],
            msg=messages,
            type="execution_error.failed",
        )


class DeviceBusy(BaseValidationException):
    def __init__(self) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body", "id"],
            msg="Device is already executing another command.",
            type="connection_error.busy",
        )


class DeviceService:
    def __init__(
        self,
        request: Request,
        http_client: httpx.AsyncClient = Depends(PlatformHttpClient()),
        event_stream: CommandExecutionEventStream = Depends(),
    ):
        self.username = request.state.username
        self.http_client = http_client
        self.event_stream = event_stream
        self.device_client = DevicePlatformClient(self.http_client)
        self.patient_client = PatientPlatformClient(self.http_client)

    async def get_devices(
        self,
        params: Optional[schemas.WebDeviceQueryParams] = None,
    ) -> schemas.WebDeviceResources:
        if params.bed_group:
            beds = await self.patient_client.get_assigned_beds_for_group(params.bed_group)
            params.bed_ids = [bed.id for bed in beds.resources]

        platform_device_resources = await self.device_client.get_devices(params.to_platform())

        return schemas.WebDeviceResources.from_platform(platform_device_resources)

    async def batch_assign_beds(self, payload: schemas.WebBatchAssignBedsSchema) -> None:
        devices_to_unassign = [device.device_id for device in payload.associations]
        devices_to_assign = [
            device.to_platform() for device in payload.associations if device.bed_id is not None
        ]
        if devices_to_unassign:
            await self.device_client.batch_unassign_beds(
                PlatformBatchUnassignBeds.model_construct(device_ids=devices_to_unassign)
            )
        if devices_to_assign:
            await self.device_client.batch_assign_beds(
                PlatformBatchAssignBeds.model_construct(associations=devices_to_assign)
            )

    async def create_or_update_device(
        self,
        payload: schemas.WebCreateOrUpdateDevice,
    ) -> None:
        devices = await self.device_client.get_devices()
        for device in devices.resources:
            if device.id == payload.id:
                await self.device_client.update_device(payload.to_platform_update())
                return None

        await self.device_client.create_device(payload.to_platform_create())

    async def get_device_vital_ranges(
        self,
        device_id: UUID,
    ) -> schemas.WebDeviceRangesResources:
        platform_ranges_resources = await self.device_client.get_device_vital_ranges(device_id)
        return schemas.WebDeviceRangesResources.from_platform(platform_ranges_resources)

    async def check_device_compatibility(
        self, payload: schemas.WebDeviceCommandSchema
    ) -> Optional[PlatformDevice]:
        # check device type
        device = await self.device_client.get_device_by_identifier(payload.pm_identifier)
        if device.gateway_id is not None:
            raise NotPatientMonitor

        # check device connection
        cache = RedisCache()
        device_cache = cache.get(f"sdc/device/primaryIdentifier/{payload.pm_identifier}")
        if device_cache is None:
            raise DeviceConnectionError
        return device

    async def run_command(self, command: schemas.WebDeviceCommandSchema, pm_id: UUID) -> None:
        organizer = CommandOrganizer()
        command_data = schemas.DeviceCommandSchema.from_payload(command, pm_id)
        event = CommandExecutionRequestEvent(self.username, command_data)
        device = await self.event_stream.add(event, command_data)
        organizer.add_request(device.request_id)

        execution_response = await wait_for_device_response(device.request_id)
        if not execution_response.success:
            raise CommandExecutionError(messages=execution_response.errors)

    async def lock_resource(
        self, payload: schemas.WebDeviceCommandSchema, request: Request
    ) -> None:
        cache_key = get_cache_key(name=f"web-command-lock-{payload.pm_identifier}", request=request)
        cache = RedisCache()
        web_cache = cache.get(cache_key)
        if web_cache is not None:
            raise DeviceBusy
        add_lock(f"web-command-lock-{payload.pm_identifier}", request)

    async def post_application_command(
        self, payload: schemas.WebDeviceCommandSchema, request: Request
    ) -> None:
        device = await self.check_device_compatibility(payload)
        try:
            await self.lock_resource(payload, request)
            await self.run_command(payload, device.id)
        finally:
            remove_lock(f"web-command-lock-{payload.pm_identifier}", request)
