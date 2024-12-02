from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request

from app.bed.repositories import ReadBedRepository
from app.bed.services import BedNotFound
from app.common import schemas as common_schemas
from app.common.exceptions import BaseValidationException
from app.device.src.common.event_sourcing.events import (
    AssignDeviceLocationEvent,
    CreateDeviceEvent,
    DeleteDeviceEvent,
    UnassignDeviceLocationEvent,
    UpdateDeviceInfoEvent,
)
from app.device.src.common.event_sourcing.stream import (
    DeviceEventStream,
    VitalRangeEventStream,
)
from app.device.src.device import schemas as device_schemas
from app.device.src.device.repository import ReadDeviceRepository, VitalsRangeRepository
from app.encounter import schemas as encounter_schemas
from app.encounter.repository import ReadEncounterRepository
from app.patient.repository import ReadPatientRepository
from app.patient.stream import BedEventStream


class DeviceAlreadyExists(BaseValidationException):
    def __init__(self) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body", "id"],
            msg="Device already exists",
            type="value_error.already_in_use",
        )


class DevicePrimaryIdentifierInUse(BaseValidationException):
    def __init__(self) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body", "primary_identifier"],
            msg="Primary identifier already in use",
            type="value_error.already_in_use",
        )


class LocationInUse(BaseValidationException):
    def __init__(self) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body", "location_id"],
            msg="Location already in use",
            type="value_error.already_in_use",
        )


class DeviceNotFound(BaseValidationException):
    def __init__(self):
        self.error = common_schemas.ErrorSchema(
            loc=["body", "device_id"],
            msg="Device not found",
            type="value_error.not_found",
        )


# pylint: disable=[R0913, R0902]
class DeviceService:
    def __init__(
        self,
        request: Request,
        event_stream: DeviceEventStream = Depends(),
        encounter_repository: ReadEncounterRepository = Depends(),
        device_repository: ReadDeviceRepository = Depends(),
        vital_stream: VitalRangeEventStream = Depends(),
        vitals_repository: VitalsRangeRepository = Depends(),
        bed_stream: BedEventStream = Depends(),
        bed_repository: ReadBedRepository = Depends(),
        patient_repository: ReadPatientRepository = Depends(),
    ):
        self.username = request.state.username
        self.device_repository = device_repository
        self.event_stream = event_stream
        self.encounter_repository = encounter_repository
        self.vital_stream = vital_stream
        self.vitals_repository = vitals_repository
        self.bed_stream = bed_stream
        self.bed_repository = bed_repository
        self.patient_repository = patient_repository

    async def get_device_by_identifier(
        self, device_id: str
    ) -> Optional[device_schemas.DeviceResource]:
        if device := await self.device_repository.get_device_by_identifier(device_id):
            return device_schemas.DeviceResource.from_orm(device)

    async def create_device(
        self, device: device_schemas.CreateDeviceSchema
    ) -> device_schemas.DeviceSchema:
        try:
            event = CreateDeviceEvent(self.username, device)
            device = await self.event_stream.add(event, None)
        except IntegrityError as exc:
            if "ix_device_primary_identifier" in exc.args[0]:
                raise DevicePrimaryIdentifierInUse from exc
            if "devices_pkey" in exc.args[0]:
                raise DeviceAlreadyExists from exc
            raise exc

        if not device.gateway_id:
            await self.vitals_repository.add_default_vital_ranges(device.id)
        return device

    async def update_device(
        self,
        payload_device: device_schemas.UpdateDeviceSchema,
    ) -> Optional[device_schemas.DeviceSchema]:
        result = None
        if found_device := await self.device_repository.get_device_by_identifier(
            payload_device.primary_identifier
        ):
            event = UpdateDeviceInfoEvent(self.username, payload_device)
            updated_device = await self.event_stream.add(event, found_device)
            result = device_schemas.DeviceSchema.from_orm(updated_device)
        return result

    async def delete_device(
        self,
        device: device_schemas.DeleteDeviceSchema,
    ):
        if found_device := await self.device_repository.get_device_by_id(
            device.device_id, include_subject=True
        ):
            event = DeleteDeviceEvent(self.username)
            patient_primary_identifier = None
            if encounter := found_device.encounter:
                patient_primary_identifier = encounter.subject.primary_identifier
            await self.event_stream.delete(
                event, found_device, related_entity_id=patient_primary_identifier
            )

    async def assign_location(self, bed_id: UUID, device_id: UUID) -> None:
        if not (device := await self.device_repository.get_device_by_id(device_id)):
            raise DeviceNotFound

        bed = await self.bed_repository.get_bed(bed_id)
        if not bed:
            raise BedNotFound

        try:
            event = AssignDeviceLocationEvent(self.username, bed)
            await self.event_stream.add(event, device)
        except IntegrityError as exc:
            if "ix_device_location" in exc.args[0] or "devices_location_key" in exc.args[0]:
                raise LocationInUse from exc
            raise exc

    async def unassign_location(self, device_id: UUID) -> None:
        if not (device := await self.device_repository.get_device_by_id(device_id)):
            raise DeviceNotFound

        if device.location_id:
            event = UnassignDeviceLocationEvent(self.username, device_id)
            await self.event_stream.add(event, device)

    async def get_all_devices(
        self,
        params: device_schemas.DeviceQueryParams,
    ) -> device_schemas.DeviceResources:
        device_list = await self.device_repository.get_all_devices(params)
        return device_schemas.DeviceResources.model_construct(
            resources=[device_schemas.DeviceResource.model_validate(d) for d in device_list]
        )

    async def get_device_vital_ranges(
        self,
        device_id: UUID,
    ) -> device_schemas.VitalRangesResources:
        ranges_list = await self.device_repository.get_device_vital_ranges(device_id)
        return device_schemas.VitalRangesResources.model_construct(
            resources=[device_schemas.VitalRange.model_validate(vrange) for vrange in ranges_list]
        )

    async def get_device_encounters(
        self,
        device_primary_identifier: str,
    ) -> encounter_schemas.AdmissionResource:
        encounter = await self.encounter_repository.get_device_encounter(device_primary_identifier)
        return encounter_schemas.AdmissionResource.model_construct(
            resource=encounter_schemas.AdmissionSchema.from_encounter(encounter)
        )
