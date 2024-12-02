from typing import List, Optional

from pydantic import BaseModel, validator

from src.common.schemas import ConfigSchema, PatientSchema
from src.emulator.emulators import DeviceDataEmulator
from src.emulator.models import PatientMonitor, Sensor
from src.sensor.schemas import ConnectedSensorPayload


class DeviceMonitorSchema(BaseModel):
    primary_identifier: str
    name: str
    patient: Optional[PatientSchema]
    connected_sensors: Optional[list[ConnectedSensorPayload]]
    config: Optional[ConfigSchema]

    @validator("config", pre=True, always=True)
    @classmethod
    def set_default_config(cls, config: ConfigSchema) -> ConfigSchema:
        return config or ConfigSchema()


class DisconnectMonitorSchema(BaseModel):
    primary_identifier: str


class PatientSessionOpenedPayload(BaseModel):
    patient_monitor_primary_identifier: str
    patient: PatientSchema


class PatientSessionClosedPayload(BaseModel):
    patient_monitor_primary_identifier: str


class EmulatorDetailSchema(BaseModel):
    name: str
    current_mode: str
    emulation_modes: List[str]

    @classmethod
    def from_emulator(
        cls, emulator: DeviceDataEmulator, current_mode: str
    ) -> "EmulatorDetailSchema":
        return cls.construct(
            name=emulator.name,
            emulation_modes=list(emulator.emulation_modes),
            current_mode=current_mode,
        )


class SensorDetailSchema(BaseModel):
    primary_identifier: str
    type: str
    name: str
    emulators: List[EmulatorDetailSchema]

    @classmethod
    def from_data_model(cls, sensor: Sensor) -> "SensorDetailSchema":
        emulators = []
        for emulator in sensor.virtual_device.emulators:
            current_mode = sensor.virtual_device.running_emulators.get(emulator.name).current_mode
            emulators.append(EmulatorDetailSchema.from_emulator(emulator, current_mode))

        return cls.construct(
            primary_identifier=sensor.primary_identifier,
            type=sensor.virtual_device.type.value,
            name=sensor.name,
            emulators=emulators,
        )


class PatientMonitorDetailSchema(BaseModel):
    primary_identifier: str
    name: str
    sensors: List[SensorDetailSchema]
    emulators: List[EmulatorDetailSchema]

    @classmethod
    def from_data_model(cls, patient_monitor: PatientMonitor) -> "PatientMonitorDetailSchema":
        emulators = []
        for emulator in patient_monitor.virtual_device.emulators:
            current_mode = patient_monitor.virtual_device.running_emulators.get(
                emulator.name
            ).current_mode
            emulators.append(EmulatorDetailSchema.from_emulator(emulator, current_mode))

        return cls.construct(
            primary_identifier=patient_monitor.primary_identifier,
            name=patient_monitor.name,
            sensors=[
                SensorDetailSchema.from_data_model(sensor) for sensor in patient_monitor.sensors
            ],
            emulators=emulators,
        )


class PatientMonitorResourcesSchema(BaseModel):
    resources: List[PatientMonitorDetailSchema]

    @classmethod
    def from_data_model(
        cls, patient_monitors: list[PatientMonitor]
    ) -> "PatientMonitorResourcesSchema":
        return cls.construct(
            resources=[
                PatientMonitorDetailSchema.from_data_model(patient_monitor)
                for patient_monitor in patient_monitors
            ]
        )
