from enum import Enum
from uuid import UUID

from pydantic import Field

from src.common.schemas_base import BaseSchema, SecretString


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class PatientSchema(BaseSchema):
    id: UUID
    primary_identifier: str = Field(alias="primaryIdentifier")
    active: bool
    given_name: SecretString = Field(alias="givenName")
    family_name: SecretString = Field(alias="familyName")
    gender: GenderEnum


class BedSchema(BaseSchema):
    id: UUID
    name: str
    patient: PatientSchema | None


class BedResourcesSchema(BaseSchema):
    resources: list[BedSchema]
