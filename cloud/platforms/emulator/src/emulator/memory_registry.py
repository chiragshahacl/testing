from typing import Dict

from src.broker import (
    publish_device_discovered,
    publish_patient_session_closed,
    publish_sensor_removed,
    publish_update_patient_monitor_configuration,
)
from src.emulator.models import Config, Patient, PatientMonitor, Sensor
from src.settings import settings


class DataManager:
    patient_registry: Dict[str, Patient]
    patient_monitors_registry: Dict[str, PatientMonitor]
    sensor_registry: Dict[str, Sensor]
    _instance = None

    def __new__(cls) -> "DataManager":
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.patient_registry = {}
            cls._instance.patient_monitors_registry = {}
            cls._instance.sensor_registry = {}
        return cls._instance

    def get_patient_monitor(self, identifier: str) -> PatientMonitor:
        patient_monitor = self.patient_monitors_registry.get(identifier)
        if not patient_monitor:
            raise KeyError(f"Patient monitor {identifier} does not exist.")

        return patient_monitor

    def get_sensor(self, identifier: str) -> Sensor:
        sensor = self.sensor_registry.get(identifier)
        if not sensor:
            raise KeyError(f"Sensor {identifier} does not exist.")

        return sensor

    async def connect_patient_monitor(self, patient_monitor: PatientMonitor):
        if len(self.patient_monitors_registry) >= settings.TOTAL_MONITORS:
            raise RuntimeError("Limit of connected patient monitors reached.")

        if self.patient_monitors_registry.get(patient_monitor.primary_identifier):
            raise RuntimeError("Patient monitor already connected.")

        if patient_monitor.sensors and not patient_monitor.patient:
            raise RuntimeError("Patient monitor with connected sensors must include the patient.")

        if patient_monitor.patient:
            patient_primary_identifier = patient_monitor.patient.primary_identifier
            if self.patient_registry.get(patient_primary_identifier):
                raise RuntimeError("Patient already assigned to a patient monitor.")

            self.patient_registry[patient_primary_identifier] = patient_monitor.patient

        self.patient_monitors_registry[patient_monitor.primary_identifier] = patient_monitor
        await patient_monitor.start_emulator()

        try:
            for sensor in patient_monitor.sensors:
                if existing_sensor := self.sensor_registry.get(sensor.primary_identifier):
                    raise RuntimeError(
                        f"Sensor already connected to "
                        f"patient monitor "
                        f"{existing_sensor.patient_monitor.primary_identifier}."
                    )

                self.sensor_registry[sensor.primary_identifier] = sensor
                await sensor.start_emulator()
        except (RuntimeError, ValueError):
            self.disconnect_patient_monitor(
                patient_monitor_identifier=patient_monitor.primary_identifier
            )
            raise
        await publish_device_discovered(patient_monitor)

    async def connect_sensor(self, patient_monitor_identifier: str, sensor: Sensor):
        patient_monitor = self.get_patient_monitor(patient_monitor_identifier)

        if not patient_monitor.patient:
            raise RuntimeError("No active patient session.")

        if existing_sensor := self.sensor_registry.get(sensor.primary_identifier):
            raise RuntimeError(
                f"Sensor already connected to "
                f"patient monitor {existing_sensor.patient_monitor.primary_identifier}."
            )

        patient_monitor.add_sensor(sensor)
        self.sensor_registry[sensor.primary_identifier] = sensor
        await publish_device_discovered(sensor)
        await sensor.start_emulator()

    async def disconnect_sensor(self, sensor_identifier):
        sensor = self.get_sensor(sensor_identifier)
        sensor.patient_monitor.remove_sensor(sensor)
        self.sensor_registry.pop(sensor_identifier)
        patient_identifier = sensor.patient.primary_identifier
        await publish_sensor_removed(sensor_identifier, sensor.device_code, patient_identifier)

    def disconnect_patient_monitor(self, patient_monitor_identifier: str):
        patient_monitor = self.get_patient_monitor(patient_monitor_identifier)
        patient_monitor.stop_emulation()
        for sensor in patient_monitor.sensors:
            self.sensor_registry.pop(sensor.primary_identifier)

        if patient_monitor.patient:
            self.patient_registry.pop(patient_monitor.patient.primary_identifier)

        self.patient_monitors_registry.pop(patient_monitor_identifier)

    async def change_patient_monitor_config(self, device_primary_identifier: str, config: Config):
        device = self.get_patient_monitor(device_primary_identifier)
        device.config = config
        await publish_update_patient_monitor_configuration(device)

    async def change_emulation_mode(
        self, device_primary_identifier: str, emulator_name: str, mode: str
    ):
        # TODO: check if the typing of emulator_name
        # and mode could be changed (instead of str)
        sensor = self.sensor_registry.get(device_primary_identifier)
        monitor = self.patient_monitors_registry.get(device_primary_identifier)
        device = monitor if monitor is not None else sensor

        if not device:
            raise KeyError(f"Device {device_primary_identifier} does not exist.")

        device.change_mode(mode, emulator_name)

    async def open_patient_session(self, patient_monitor_primary_identifier, patient: Patient):
        existing_patient = self.patient_registry.get(patient.primary_identifier)
        patient_monitor = self.get_patient_monitor(patient_monitor_primary_identifier)

        if patient_monitor.patient:
            raise RuntimeError("Already active patient session.")

        if existing_patient:
            raise RuntimeError("Patient already assigned to a patient monitor.")

        patient_monitor.patient = patient

        self.patient_registry[patient.primary_identifier] = patient
        self.patient_monitors_registry[patient_monitor.primary_identifier] = patient_monitor
        await publish_device_discovered(patient_monitor)

    async def close_patient_session(self, patient_monitor_primary_identifier):
        patient_monitor = self.get_patient_monitor(patient_monitor_primary_identifier)

        if not patient_monitor.patient:
            raise RuntimeError("No active patient session.")

        for sensor in patient_monitor.sensors:
            patient_monitor.remove_sensor(sensor)
            self.sensor_registry.pop(sensor.primary_identifier)

        patient_primary_identifier = patient_monitor.patient.primary_identifier
        self.patient_registry.pop(patient_primary_identifier)
        patient_monitor.patient = None

        await publish_patient_session_closed(
            patient_monitor_primary_identifier, patient_primary_identifier
        )
