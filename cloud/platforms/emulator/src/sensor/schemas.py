from pydantic import BaseModel

from src.emulator.constants import (
    DeviceEmulationModes,
    DeviceEmulationNames,
    DeviceTypes,
)


class ConnectedSensorPayload(BaseModel):
    primary_identifier: str
    name: str
    device_code: DeviceTypes


class DeviceSensorSchema(BaseModel):
    primary_identifier: str
    patient_monitor_primary_identifier: str
    name: str
    device_code: DeviceTypes


class DisconnectSensorSchema(BaseModel):
    primary_identifier: str


class UpdateSensorModeWebSchema(BaseModel):
    primary_identifier: str
    emulator_name: DeviceEmulationNames
    mode: DeviceEmulationModes
