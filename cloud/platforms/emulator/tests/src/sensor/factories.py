from typing import Optional

from faker import Faker
from polyfactory.decorators import post_generated
from polyfactory.factories.pydantic_factory import ModelFactory

from src.emulator.constants import (
    DeviceEmulationModes,
    DeviceEmulationNames,
    DeviceTypes,
)
from src.sensor.schemas import (
    ConnectedSensorPayload,
    DeviceSensorSchema,
    UpdateSensorModeWebSchema,
)
from src.settings import settings


class DeviceSensorSchemaFactory(ModelFactory[DeviceSensorSchema]):
    Faker.seed(settings.FAKE_DATA_SEED)
    __model__ = DeviceSensorSchema
    __fake__ = Faker()

    @classmethod
    def primary_identifier(cls) -> str:
        return f"SEN-EM-{str(cls.__fake__.uuid4())}"

    @post_generated
    @classmethod
    def name(cls, primary_identifier: str) -> str:
        return f"Sensor {primary_identifier}"

    @classmethod
    def patient_monitor_primary_identifier(cls) -> Optional[str]:
        return f"PM-EM-{str(cls.__fake__.uuid4())}"

    @classmethod
    def device_code(cls) -> str:
        sensor_types = [
            device_type.value
            for device_type in DeviceTypes
            if device_type is not DeviceTypes.PATIENT_MONITOR
        ]
        return cls.__fake__.random_element(sensor_types)


class UpdateSensorModeWebSchemaFactory(ModelFactory[UpdateSensorModeWebSchema]):
    Faker.seed(settings.FAKE_DATA_SEED)
    __model__ = UpdateSensorModeWebSchema
    __fake__ = Faker()

    @classmethod
    def primary_identifier(cls) -> str:
        return f"SEN-EM-{str(cls.__fake__.uuid4())}"

    @classmethod
    def emulator_name(cls) -> str:
        emulator_names = [emulator_name.value for emulator_name in DeviceEmulationNames]
        return cls.__fake__.random_element(emulator_names)

    @classmethod
    def mode(cls) -> str:
        modes = [emulator_mode.value for emulator_mode in DeviceEmulationModes]
        return cls.__fake__.random_element(modes)


class ConnectedSensorPayloadFactory(ModelFactory[ConnectedSensorPayload]):
    Faker.seed(settings.FAKE_DATA_SEED)
    __model__ = ConnectedSensorPayload
    __fake__ = Faker()

    @classmethod
    def primary_identifier(cls) -> str:
        return f"SEN-EM-{str(cls.__fake__.uuid4())}"

    @post_generated
    @classmethod
    def name(cls, primary_identifier: str) -> str:
        return f"Sensor {primary_identifier}"

    @classmethod
    def device_code(cls) -> str:
        sensor_types = [
            device_type.value
            for device_type in DeviceTypes
            if device_type is not DeviceTypes.PATIENT_MONITOR
        ]
        return cls.__fake__.random_element(sensor_types)
