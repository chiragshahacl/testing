from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from common_schemas import SecretDate, SecretString
from common_schemas.dates import DateISO8601
from pydantic import Field, StringConstraints
from pydantic.types import Decimal
from typing_extensions import Annotated

from src.common.platform.patient.enums import GenderEnum
from src.common.schemas import BaseSchema


class PlatformPatient(BaseSchema):
    id: UUID
    primary_identifier: str
    active: bool
    given_name: SecretString
    family_name: SecretString
    gender: GenderEnum
    birth_date: Optional[SecretDate] = None


class CreatePatientSchema(BaseSchema):
    id: UUID
    primary_identifier: Annotated[str, StringConstraints(min_length=1, max_length=255)] = Field(
        alias="primaryIdentifier"
    )
    active: bool
    given_name: Annotated[SecretString, StringConstraints(min_length=1, max_length=255)] = Field(
        alias="givenName"
    )
    family_name: SecretString = Field(alias="familyName")
    gender: GenderEnum
    birth_date: Optional[SecretDate] = Field(alias="birthDate", default=None)


class DeletePatientSchema(BaseSchema):
    id: UUID


class UpsertPatientSchema(CreatePatientSchema):
    pass


class PlatformPatientResources(BaseSchema):
    resources: List[PlatformPatient]


class PlatformGetPatientObservations(BaseSchema):
    isAlert: bool
    patientIds: List[str]


class PlatformGetEHRPatientParams(BaseSchema):
    patient_identifier: str | None = Field(default=None, alias="patientIdentifier")
    given_name: str | None = Field(default=None, alias="givenName")
    family_name: str | None = Field(default=None, alias="familyName")
    birth_date: DateISO8601 | None = Field(default=None, alias="birthDate")

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        data = super().model_dump(*args, **kwargs)
        if data.get("birthDate"):
            data["birthDate"] = data["birthDate"].isoformat().replace("-", "")
        return data


class EHRPatient(BaseSchema):
    patient_identifiers: list[str] | None = Field(default=[], alias="patientIdentifiers")
    given_name: str | None = Field(default=None, alias="givenName")
    family_name: str | None = Field(default=None, alias="familyName")
    birth_date: DateISO8601 | None = Field(default=None, alias="birthDate")
    gender: str | None = None

    @property
    def patient_primary_identifier(self) -> str:
        # pylint: disable=E1136
        return self.patient_identifiers[0]


class PlatformEHRPatientResources(BaseSchema):
    resources: list[EHRPatient] | None = []


class PlatformPatientObservation(BaseSchema):
    id: UUID
    category: str
    code: str
    subject_id: str
    effective_dt: datetime
    value_number: Optional[Decimal] = None
    value_text: Optional[str] = None
    device_primary_identifier: Optional[str]
    device_code: Optional[str]


class PlatformPatientObservationsResources(BaseSchema):
    resources: List[PlatformPatientObservation]


class PlatformPatientPhysiologicalAlert(BaseSchema):
    code: str
    start_determination_time: datetime
    end_determination_time: datetime
    value_text: str
    device_primary_identifier: str
    device_code: str
    trigger_lower_limit: Optional[float]
    trigger_upper_limit: Optional[float]


class PlatformEncounter(BaseSchema):
    id: UUID
    subject_id: UUID
    device_id: UUID
    created_at: datetime
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class PlatformDeletePatientAdmissionSchema(BaseSchema):
    patient_id: UUID


class PlatformEncounterPatientAdmissionSchema(BaseSchema):
    subject_id: UUID
    bed_id: UUID
