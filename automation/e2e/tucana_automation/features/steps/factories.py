from datetime import date
from typing import Optional, List
import enum
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory import PostGenerated
from pydantic import BaseModel
from uuid import UUID


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


# Web models
class CreateOrUpdateDevice(BaseModel):
    id: UUID
    name: str
    primary_identifier: str
    device_code: str = "Patient Monitor"


class Config(BaseModel):
    audio_pause_enabled: bool = False
    audio_enabled: bool = True


def override_name(device_name):
    def inner(name, values, *args, **kwargs):
        return f"{device_name}: {values['primary_identifier']}"

    return inner


class CreateOrUpdateDeviceFactory(ModelFactory[CreateOrUpdateDevice]):
    __model__ = CreateOrUpdateDevice

    name = PostGenerated(override_name("Patient Monitor"))


# Emulator models


class PatientSchema(BaseModel):
    primary_identifier: str
    given_name: str
    family_name: str
    gender: GenderEnum
    birth_date: Optional[date]


class DeviceTypes(str, enum.Enum):
    ADAM = "ADAM"
    ANNE_CHEST = "ANNE Chest"
    ANNE_LIMB = "ANNE Limb"
    NONIN_3150 = "Nonin 3150"
    VIATOM_BP = "Viatom BP monitor"
    JOYTECH_THERMOMETER = "DMT Thermometer"
    PATIENT_MONITOR = "Patient Monitor"


class ConnectedSensors(BaseModel):
    primary_identifier: str
    name: str
    device_code: DeviceTypes


class Sensor(BaseModel):
    primary_identifier: str
    patient_monitor_primary_identifier: str
    name: str
    device_code: DeviceTypes


class OpenPatientSession(BaseModel):
    patient_monitor_primary_identifier: str
    patient: PatientSchema


class OpenPatientSessionFactory(ModelFactory[OpenPatientSession]):
    __model__ = OpenPatientSession


class ConnectSensorFactory(ModelFactory[OpenPatientSession]):
    __model__ = Sensor
    name = PostGenerated(override_name("Sensor"))


class DeviceEmulationNames(str, enum.Enum):
    MONITOR_CONNECTION_STATUS = "MONITOR_CONNECTION_STATUS"
    BLOOD_PRESSURE = "BLOOD_PRESSURE"
    HEART_RATE = "HEART_RATE_EMULATOR"
    ECG = "ECG_EMULATOR"
    CARDIAC = "CARDIAC_EMULATOR"
    BLOOD_OXYGEN = "BLOOD_OXYGEN_EMULATOR"
    PULSE = "PULSE_EMULATOR"
    PULSE_RATE = "PULSE_RATE_EMULATOR"
    PERFUSION_INDEX = "PERFUSION_INDEX_EMULATOR"
    BODY_TEMPERATURE = "BODY_TEMPERATURE_EMULATOR"
    CHEST_TEMPERATURE = "CHEST_TEMPERATURE_EMULATOR"
    LIMB_TEMPERATURE = "LIMB_TEMPERATURE_EMULATOR"
    FALLS = "FALLS_EMULATOR"
    POSITION = "POSITION_EMULATOR"
    RESPIRATORY_RATE = "RESPIRATORY_RATE_EMULATOR"
    PLETH = "PLETH_EMULATOR"
    SENSOR_SIGNAL = "SENSOR_SIGNAL_EMULATOR"
    SENSOR_BATTERY = "SENSOR_BATTERY_EMULATOR"
    SENSOR_MODULE_STATE = "SENSOR_MODULE_STATE_EMULATOR"
    SENSOR_LEAD_STATE = "SENSOR_LEAD_STATE_EMULATOR"
    SENSOR_CONTACT_STATE = "SENSOR_CONTACT_STATE_EMULATOR"
    SENSOR_CONNECTION_STATE = "SENSOR_CONNECTION_STATE_EMULATOR"


class DeviceEmulationModes(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    ERROR = "error"
    FIXED = "fixed"


class UpdateSensorMode(BaseModel):
    primary_identifier: str
    emulator_name: DeviceEmulationNames
    mode: DeviceEmulationModes


class UpdateSensorModeFactory(ModelFactory[UpdateSensorMode]):
    __model__ = UpdateSensorMode


class ConnectPatientMonitor(BaseModel):
    primary_identifier: str
    name: str
    patient: PatientSchema
    connected_sensors: List[ConnectedSensors] = []
    config: Optional[Config]


class ConnectPatientMonitorFactory(ModelFactory[ConnectPatientMonitor]):
    __model__ = ConnectPatientMonitor
    name = PostGenerated(override_name("Patient Monitor"))
    device_code = "Patient Monitor"
