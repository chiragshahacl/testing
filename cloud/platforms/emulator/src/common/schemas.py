from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, validator

from src.common.constants import GenderEnum
from src.emulator.constants import (
    AlarmCodes,
    AlarmPriorities,
    DeviceTypes,
)


class PatientSchema(BaseModel):
    primary_identifier: str
    given_name: str
    family_name: str
    gender: GenderEnum
    birth_date: Optional[date]


class PatientEncryptedSchema(BaseModel):
    primary_identifier: str
    given_name: str
    family_name: str
    gender: GenderEnum
    birth_date: Optional[str]

    @validator("given_name")
    def encrypt_str(cls, value):  # pylint: disable=E0213
        return value

    @validator("family_name")
    def remove_whitespace(cls, value):  # pylint: disable=E0213
        return value

    @validator("birth_date", pre=True)
    def encrypt_date(cls, value):  # pylint: disable=E0213
        return value.isoformat() if value else None


class ConfigSchema(BaseModel):
    audio_pause_enabled: bool = False
    audio_enabled: bool = True


class ConnectedSensorSchema(BaseModel):
    primary_identifier: str
    name: str
    device_code: DeviceTypes


class DeviceSchema(BaseModel):
    primary_identifier: str
    name: str
    device_code: DeviceTypes
    connected_sensors: Optional[list[ConnectedSensorSchema]]
    config: Optional[ConfigSchema] = {}
    gateway_id: str = None


class BrokerMessageWrapper(BaseModel):
    message_id: str
    event_name: str
    event_type: str
    timestamp: str
    payload: dict

    class Config:
        use_enum_values = True


class BrokerMessage(BaseModel):
    topic: str
    value: BrokerMessageWrapper
    key: str
    headers: list[tuple[str, bytes], ...]


class MetricsPayloadSchema(BaseModel):
    patient_primary_identifier: str
    samples: list
    determination_time: datetime
    code: str
    device_code: str
    unit_code: str
    device_primary_identifier: str


class MetricsBrokerMessageSchema(BrokerMessageWrapper):
    payload: MetricsPayloadSchema


class DeviceConnectedSchema(BrokerMessageWrapper):
    event_type = "DEVICE_DISCOVERED"
    event_name = "Device discovered"


class DeviceConnectedPayloadSchema(BaseModel):
    device: DeviceSchema
    patient: PatientEncryptedSchema | None


class SensorRemovedSchema(BrokerMessageWrapper):
    event_type = "SENSOR_REMOVED_EVENT"
    event_name = "Sensor removed"


class SensorRemovedPayloadSchema(BaseModel):
    device_primary_identifier: str
    device_type: str
    patient_primary_identifier: str
    determination_time: str


class PatientSessionClosedSchema(BrokerMessageWrapper):
    event_type = "PATIENT_SESSION_CLOSED_EVENT"
    event_name = "Patient session closed"


class PatientSessionClosedPayloadSchema(BaseModel):
    patient_primary_identifier: str
    device_primary_identifier: str


class AlertSchema(BrokerMessageWrapper):
    event_type = "NEW_ALERT_OBSERVATION"
    event_name = "New alert observation"


class AlertRangeSchema(BaseModel):
    code: str
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None
    alert_condition_enabled: bool


class AlertPayloadSchema(BaseModel):
    patient_primary_identifier: str
    device_primary_identifier: str
    device_code: DeviceTypes
    code: AlarmCodes
    priority: AlarmPriorities
    determination_time: str
    active: bool
    latching: bool
    vital_range: Optional[AlertRangeSchema] = None


class UpdatePatientMonitorConfigSchema(BrokerMessageWrapper):
    event_type = "PM_CONFIGURATION_UPDATED"
    event_name = "PM configuration updated"


class UpdatePatientMonitorConfigPayload(BaseModel):
    device_primary_identifier: str
    audio_enabled: bool = True
    audio_pause_enabled: bool = False


class PatientAdmissionRejectedSchema(BrokerMessageWrapper):
    event_name = "Patient admission rejected"
    event_type = "PATIENT_ADMISSION_REJECTED"


class PatientAdmissionRejectedPayload(BaseModel):
    device_primary_identifier: str
    patient_primary_identifier: str
