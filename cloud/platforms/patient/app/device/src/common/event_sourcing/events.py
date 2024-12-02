from typing import Optional
from uuid import UUID

from app.common.event_sourcing.events import Event
from app.common.models import Bed
from app.device.src.common.models import Device, DeviceAlert, DeviceVitalRange
from app.device.src.device.schemas import (
    CreateDeviceAlertSchema,
    CreateDeviceSchema,
    CreateVitalRangeSchema,
    UpdateDeviceAlertSchema,
    UpdateDeviceSchema,
)


class CreateDeviceEvent(Event):
    display_name: str = "Device Created"
    event_type: str = "DEVICE_CREATED_EVENT"
    is_backfill: str = "0"

    def __init__(self, username: str, payload: CreateDeviceSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, _: Optional[Device] = None) -> Device:
        device = Device(
            id=self.payload.id,
            primary_identifier=self.payload.primary_identifier,
            name=self.payload.name,
            gateway_id=self.payload.gateway_id,
            model_number=self.payload.model_number,
            audio_pause_enabled=self.payload.audio_pause_enabled,
            audio_enabled=self.payload.audio_enabled,
        )
        return device


class DeleteDeviceEvent(Event):
    display_name: str = "Device deleted"
    event_type: str = "DEVICE_DELETED_EVENT"
    is_backfill: str = "0"

    def process(self, entity: Device) -> Device:
        return entity


class UpdateDeviceInfoEvent(Event):
    display_name: str = "Device information updated"
    event_type: str = "DEVICE_UPDATED_EVENT"
    is_backfill: str = "0"

    def __init__(self, username: str, payload: UpdateDeviceSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, entity: Device) -> Device:
        entity.name = self.payload.name
        entity.gateway_id = self.payload.gateway_id
        entity.subject_identifier = self.payload.subject_identifier
        entity.model_number = self.payload.model_number
        entity.audio_pause_enabled = self.payload.audio_pause_enabled
        entity.audio_enabled = self.payload.audio_enabled
        return entity


class UpdateDeviceConfigEvent(Event):
    display_name: str = "Device configuration updated"
    event_type: str = "DEVICE_CONFIG_UPDATED_EVENT"
    is_backfill: str = "0"

    def __init__(self, username: str, audio_pause_enabled: bool, audio_enabled: bool):
        super().__init__(username)
        self.audio_enabled = audio_enabled
        self.audio_pause_enabled = audio_pause_enabled

    def process(self, entity: Device) -> Device:
        entity.audio_pause_enabled = self.audio_pause_enabled
        entity.audio_enabled = self.audio_enabled
        return entity


class AssignDeviceLocationEvent(Event):
    display_name: str = "Assign location to device"
    event_type: str = "ASSIGN_DEVICE_LOCATION_EVENT"
    is_backfill: str = "0"

    def __init__(self, username: str, bed: Bed):
        super().__init__(username)
        self.bed = bed

    def process(self, entity: Device) -> Device:
        entity.location = self.bed
        return entity


class UnassignDeviceLocationEvent(Event):
    display_name: str = "Unassign location"
    event_type: str = "UNASSIGN_DEVICE_LOCATION_EVENT"
    is_backfill: str = "0"

    def __init__(self, username: str, device_id: UUID):
        super().__init__(username)
        self.device_id = device_id

    def process(self, entity: Device) -> Device:
        entity.location = None
        entity.location_id = None
        return entity


class CreateVitalRangeEvent(Event):
    display_name: str = "Vital Range Created"
    event_type: str = "VITAL_RANGE_CREATED_EVENT"
    is_backfill: str = "0"

    def __init__(self, username: str, payload: CreateVitalRangeSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, _: Optional[DeviceVitalRange] = None) -> DeviceVitalRange:
        device_vital_range = DeviceVitalRange(
            id=self.payload.id,
            code=self.payload.code,
            upper_limit=self.payload.upper_limit,
            lower_limit=self.payload.lower_limit,
            alert_condition_enabled=self.payload.alert_condition_enabled,
            device_id=self.payload.device_id,
        )
        return device_vital_range


class DeleteVitalRangeEvent(Event):
    display_name: str = "Device information updated"
    event_type: str = "VITAL_RANGE_DELETED_EVENT"
    is_backfill: str = "0"

    def process(self, entity: DeviceVitalRange) -> DeviceVitalRange:
        return entity


class CreateDeviceAlertEvent(Event):
    display_name: str = "Device Alert Created"
    event_type: str = "DEVICE_ALERT_CREATED"
    is_backfill: str = "0"

    def __init__(self, username: str, payload: CreateDeviceAlertSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, _: Optional[DeviceAlert]) -> DeviceAlert:
        device_alert = DeviceAlert(
            id=self.payload.id,
            code=self.payload.code,
            device_id=self.payload.device_id,
            priority=self.payload.priority,
        )
        return device_alert


class UpdateDeviceAlertEvent(Event):
    display_name: str = "Device Alert Updated"
    event_type: str = "DEVICE_ALERT_UPDATED"
    is_backfill: str = "0"

    def __init__(self, username: str, payload: UpdateDeviceAlertSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, entity: DeviceAlert) -> DeviceAlert:
        entity.code = self.payload.code
        entity.device_id = self.payload.device_id
        entity.priority = self.payload.priority
        return entity


class DeleteDeviceAlertEvent(Event):
    display_name: str = "Device Alert Deleted"
    event_type: str = "DEVICE_ALERT_DELETED"
    is_backfill: str = "0"

    def process(self, entity: DeviceAlert) -> DeviceAlert:
        return entity


class DeviceAlertsUpdatedEvent(Event):
    display_name: str = "Multiple Device Alerts Updated"
    event_type: str = "MULTIPLE_DEVICE_ALERTS_UPDATED"
    is_backfill: str = "0"

    def process(self, entity: DeviceAlert) -> DeviceAlert:
        return entity


class BackfillDeviceVitalRangeEvent(Event):
    display_name: str = "Vital Range Created"
    event_type: str = "VITAL_RANGE_CREATED_EVENT"
    is_backfill: str = "1"

    def process(self, entity: DeviceVitalRange) -> DeviceVitalRange:
        return entity
