import asyncio
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from src.emulator.constants import DeviceEmulationModes, DeviceEmulationNames
from src.emulator.task_proxy import TaskManager
from src.emulator.virtual_devices import VirtualDevice
from src.settings import settings


@dataclass
class Patient:
    primary_identifier: str
    birth_date: date | None
    given_name: str = "-"
    family_name: str = "-"
    gender: str = "Unknown"


@dataclass
class Config:
    audio_pause_enabled: bool = False
    audio_enabled: bool = True


@dataclass(kw_only=True)
class Device:
    primary_identifier: str
    name: str
    device_code: str
    patient: Patient | None = None
    base_task: asyncio.Task | None = None
    virtual_device: VirtualDevice | None = None

    async def start_emulator(self) -> None:
        patient_primary_identifier = self.patient.primary_identifier if self.patient else None
        base_task, virtual_device = TaskManager.start_emulation(
            patient_primary_identifier, self.primary_identifier, self.device_code
        )
        self.base_task = base_task
        self.virtual_device = virtual_device

    def change_mode(self, mode: DeviceEmulationModes, emulator_name: DeviceEmulationNames):
        modes = self.virtual_device.get_emulation_modes()

        if self.virtual_device.has_emulator(emulator_name):
            modes[emulator_name] = DeviceEmulationModes(mode)
        else:
            raise ValueError(f"Device {self.primary_identifier} has not {emulator_name} emulator.")

        TaskManager.stop_emulation(self.base_task, self.virtual_device)

        base_task, virtual_device = TaskManager.start_emulation(
            self.patient.primary_identifier,
            self.primary_identifier,
            self.device_code,
            modes=modes,
        )
        self.base_task = base_task
        self.virtual_device = virtual_device


@dataclass
class Sensor(Device):
    patient_monitor: Optional["PatientMonitor"] = None

    def stop_emulation(self) -> None:
        TaskManager.stop_emulation(self.base_task, self.virtual_device)


@dataclass
class PatientMonitor(Device):
    device_code: str = field(default="Patient Monitor")
    sensors: list[Sensor] = field(default_factory=lambda: [])
    config: Optional[Config] = None

    def add_sensor(self, sensor: Sensor) -> None:
        if len(self.sensors) >= settings.TOTAL_SENSORS_PER_MONITOR:
            raise RuntimeError("Limit of connected sensors reached.")
        sensor.patient = self.patient
        sensor.patient_monitor = self
        self.sensors.append(sensor)

    def remove_sensor(self, sensor: Sensor):
        self.sensors.remove(sensor)
        sensor.stop_emulation()

    def stop_emulation(self) -> None:
        for sensor in self.sensors:
            sensor.stop_emulation()
        TaskManager.stop_emulation(self.base_task, self.virtual_device)
