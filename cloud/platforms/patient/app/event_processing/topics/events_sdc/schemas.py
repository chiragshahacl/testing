from datetime import date, datetime
from typing import Any, Dict, Optional

from common_schemas import SecretDateString, SecretString
from common_schemas.dates import TimezoneFreeDatetime
from pydantic import ConfigDict

from app.common.schemas import BaseSchema
from app.patient.enums import GenderEnum


class SDCIncomingMessage(BaseSchema):
    message_id: str
    event_name: str
    event_type: str
    timestamp: datetime
    payload: Dict[str, Any]


class SDCSensorPayload(BaseSchema):
    primary_identifier: str
    name: str
    device_code: str


class SDCDeviceConfigPayload(BaseSchema):
    audio_enabled: bool
    audio_pause_enabled: bool


class SDCVitalsRange(BaseSchema):
    code: str
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None
    alert_condition_enabled: bool
    is_backfill: bool = False


class SDCNewVitalsRangesPayload(BaseSchema):
    primary_identifier: str
    ranges: list[SDCVitalsRange]


class SDCNewVitalsRangesEvent(SDCIncomingMessage):
    payload: SDCNewVitalsRangesPayload


class SDCAlertPayload(BaseSchema):
    patient_primary_identifier: str
    active: bool
    latching: bool
    code: str
    priority: str
    determination_time: TimezoneFreeDatetime
    device_primary_identifier: str
    device_code: Optional[str] = None
    is_backfill: Optional[bool] = False
    vital_range: Optional[SDCVitalsRange] = None


class SDCDevicePayload(BaseSchema):
    primary_identifier: str
    name: str
    gateway_id: Optional[str] = None
    device_code: str
    connected_sensors: Optional[list[SDCSensorPayload]] = []
    alerts: Optional[list[SDCAlertPayload]] = []
    config: SDCDeviceConfigPayload


class SDCPatientPayload(BaseSchema):
    primary_identifier: str
    given_name: SecretString
    family_name: SecretString
    gender: GenderEnum
    birth_date: Optional[SecretDateString] = None
    alerts: Optional[list[SDCAlertPayload]] = []

    @property
    def given_name_decrypted(self) -> str:
        return self.given_name.get_secret_value()

    @property
    def family_name_decrypted(self) -> str:
        return self.family_name.get_secret_value()

    @property
    def birth_date_decrypted(self) -> Optional[date]:
        return date.fromisoformat(self.birth_date.get_secret_value()) if self.birth_date else None


class SDCDeviceDiscoveredPayload(BaseSchema):
    device: SDCDevicePayload
    patient: Optional[SDCPatientPayload] = None


class SDCDeviceDiscoveredEvent(SDCIncomingMessage):
    payload: SDCDeviceDiscoveredPayload


class SDCPatientSessionClosedPayload(BaseSchema):
    device_primary_identifier: str
    patient_primary_identifier: Optional[str] = None


class SDCPatientSessionClosedEvent(SDCIncomingMessage):
    payload: SDCPatientSessionClosedPayload


class SDCSensorRemovedPayload(BaseSchema):
    device_primary_identifier: str
    patient_primary_identifier: str
    determination_time: str


class SDCSensorRemovedEvent(SDCIncomingMessage):
    payload: SDCSensorRemovedPayload


class SDCPatientMonitorConfigurationUpdatedPayload(SDCDeviceConfigPayload):
    device_primary_identifier: str


class SDCPatientMonitorConfigurationUpdatedEvent(SDCIncomingMessage):
    payload: SDCPatientMonitorConfigurationUpdatedPayload


class SDCPatientSessionStartedPayload(BaseSchema):
    patient_monitor_identifier: str
    patient: SDCPatientPayload


class SDCPatientSessionStartedEvent(SDCIncomingMessage):
    payload: SDCPatientSessionStartedPayload


class SDCPatientAdmissionRejectedPayload(BaseSchema):
    model_config = ConfigDict(str_strip_whitespace=True)

    device_primary_identifier: str
    patient_primary_identifier: str


class SDCPatientAdmissionEvent(SDCIncomingMessage):
    payload: SDCPatientAdmissionRejectedPayload
