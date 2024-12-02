from typing import Optional

from faker import Faker
from polyfactory.decorators import post_generated
from polyfactory.factories.pydantic_factory import ModelFactory

from src.common.constants import GenderEnum
from src.common.schemas import ConfigSchema, PatientSchema
from src.monitor.schemas import (
    DeviceMonitorSchema,
    PatientSessionOpenedPayload,
)
from src.settings import settings


class ConfigSchemaFactory(ModelFactory[ConfigSchema]):
    Faker.seed(settings.FAKE_DATA_SEED)
    __model__ = ConfigSchema
    __fake__ = Faker()

    @classmethod
    def audio_pause_enabled(cls) -> bool:
        return False

    @classmethod
    def audio_enabled(cls) -> bool:
        return True


class DeviceMonitorSchemaFactory(ModelFactory[DeviceMonitorSchema]):
    Faker.seed(settings.FAKE_DATA_SEED)
    __model__ = DeviceMonitorSchema
    __fake__ = Faker()

    @classmethod
    def primary_identifier(cls) -> str:
        return f"PM-EM-{str(cls.__fake__.uuid4())}"

    @classmethod
    def patient(cls) -> Optional[PatientSchema]:
        return None

    @classmethod
    def connected_sensors(cls) -> Optional[list]:
        return None

    @classmethod
    def config(cls) -> Optional[ConfigSchema]:
        return None

    @post_generated
    @classmethod
    def name(cls, primary_identifier: str) -> str:
        return f"Patient monitor {primary_identifier}"


class PatientSchemaFactory(ModelFactory[PatientSchema]):
    Faker.seed(settings.FAKE_DATA_SEED)
    __model__ = PatientSchema
    __fake__ = Faker()

    @classmethod
    def primary_identifier(cls) -> str:
        return f"P-EM-{str(cls.__fake__.uuid4())}"

    @classmethod
    def gender(cls) -> str:
        return cls.__fake__.random_element(GenderEnum)

    @post_generated
    @classmethod
    def given_name(cls, gender: str) -> str:
        if gender == GenderEnum.FEMALE:
            return cls.__fake__.first_name_female()
        elif gender == GenderEnum.MALE:
            return cls.__fake__.first_name_male()
        else:
            return cls.__fake__.first_name()

    @post_generated
    @classmethod
    def family_name(cls, gender: str) -> str:
        if gender == GenderEnum.FEMALE:
            return cls.__fake__.first_name_female()
        elif gender == GenderEnum.MALE:
            return cls.__fake__.first_name_male()
        else:
            return cls.__fake__.first_name()

    @classmethod
    def birth_date(cls) -> Optional[str]:
        return cls.__fake__.date_of_birth(minimum_age=1, maximum_age=90)


class PatientSessionOpenedPayloadFactory(ModelFactory[PatientSessionOpenedPayload]):
    Faker.seed(settings.FAKE_DATA_SEED)
    __model__ = PatientSessionOpenedPayload
    __fake__ = Faker()

    @classmethod
    def patient_monitor_primary_identifier(cls) -> str:
        return f"PM-EM-{str(cls.__fake__.uuid4())}"

    @classmethod
    def patient(cls) -> PatientSchema:
        return PatientSchemaFactory().build()
