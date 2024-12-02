import secrets
import uuid
from datetime import datetime
from typing import List, Literal, Optional, Union
from uuid import UUID

from common_schemas import SecretDate, SecretString
from common_schemas.dates import DateISO8601
from pydantic import Field

from src.common.platform.patient import schemas as platform_patient_schemas
from src.common.platform.patient.enums import GenderEnum, HL7GenderEnum
from src.common.platform.patient.schemas import UpsertPatientSchema
from src.common.schemas import WebBaseSchema


class WebPatient(WebBaseSchema):
    id: UUID
    primary_identifier: str = Field(alias="primaryIdentifier")
    active: bool
    given_name: SecretString = Field(alias="givenName")
    family_name: SecretString = Field(alias="familyName")
    gender: GenderEnum
    birth_date: Optional[SecretDate] = Field(alias="birthDate", default=None)

    @classmethod
    def from_platform(cls, patient: platform_patient_schemas.PlatformPatient):
        return cls.model_construct(
            id=patient.id,
            primary_identifier=patient.primary_identifier,
            active=patient.active,
            given_name=patient.given_name,
            family_name=patient.family_name,
            gender=patient.gender,
            birth_date=patient.birth_date,
        )


class WebPatientResources(WebBaseSchema):
    resources: List[WebPatient]

    @classmethod
    def from_platform(
        cls, patients: platform_patient_schemas.PlatformPatientResources
    ) -> "WebPatientResources":
        return cls.model_construct(
            resources=[WebPatient.from_platform(p) for p in patients.resources]
        )


class WebGetPatientAlerts(WebBaseSchema):
    isAlert: bool
    patientIds: List[str]

    def to_platform(self) -> platform_patient_schemas.PlatformGetPatientObservations:
        return platform_patient_schemas.PlatformGetPatientObservations.model_construct(
            isAlert=self.isAlert,
            patientIds=self.patientIds,
        )


# pylint: disable=R0801
class WebSessionAlert(WebBaseSchema):
    code: str
    start_determination_time: datetime = Field(alias="startDeterminationTime")
    end_determination_time: datetime = Field(alias="endDeterminationTime")
    value_text: str = Field(alias="valueText")
    device_primary_identifier: str | None = Field(alias="devicePrimaryIdentifier", default=None)
    device_code: str = Field(alias="deviceCode")
    trigger_lower_limit: Optional[float] = Field(alias="triggerLowerLimit", default=None)
    trigger_upper_limit: Optional[float] = Field(alias="triggerUpperLimit", default=None)


class WebSessionAlertResources(WebBaseSchema):
    resources: List[WebSessionAlert]


class WebEncounter(WebBaseSchema):
    subject_id: UUID = Field(alias="subjectId")
    device_id: UUID = Field(alias="deviceId")
    created_at: datetime = Field(alias="createdAt")
    status: str
    start_time: Optional[datetime] = Field(default=None, alias="startTime")
    end_time: Optional[datetime] = Field(default=None, alias="endTime")

    @classmethod
    def from_platform(
        cls, platform_encounter: platform_patient_schemas.PlatformEncounter
    ) -> "WebEncounter":
        return cls.model_validate(platform_encounter)


class WebQuickAdmitPayload(WebBaseSchema):
    type: Literal["quick-admit"] = "quick-admit"
    given_name: str | None = Field(default=None, alias="givenName")
    family_name: str | None = Field(default=None, alias="familyName")
    birth_date: Optional[DateISO8601] = Field(default=None, alias="birthDate")
    gender: Optional[GenderEnum] = GenderEnum.UNKNOWN

    def to_upsert_patient_payload(self) -> UpsertPatientSchema:
        return UpsertPatientSchema(
            id=uuid.uuid4(),
            primary_identifier=secrets.token_urlsafe(12),
            given_name=self.given_name,
            family_name=self.family_name,
            birth_date=self.birth_date,
            active=True,
            gender=self.gender,
        )


HL7_TO_FHIR_GENDER_MAPPING = {
    HL7GenderEnum.MALE: GenderEnum.MALE,
    HL7GenderEnum.FEMALE: GenderEnum.FEMALE,
    HL7GenderEnum.AMBIGUOUS: GenderEnum.OTHER,
    HL7GenderEnum.NOT_APPLICABLE: GenderEnum.UNKNOWN,
    HL7GenderEnum.OTHER: GenderEnum.OTHER,
    HL7GenderEnum.UNKNOWN: GenderEnum.UNKNOWN,
}


class WebEHRAdmitPayload(WebBaseSchema):
    type: Literal["ehr-search"] = "ehr-search"
    patient_identifier: str = Field(..., alias="patientIdentifier")
    given_name: Optional[str] = Field(default="-", alias="givenName")
    family_name: Optional[str] = Field(default="-", alias="familyName")
    birth_date: Optional[DateISO8601] = Field(default=None, alias="birthDate")
    gender: Optional[HL7GenderEnum] = Field(default=HL7GenderEnum.UNKNOWN)

    def to_upsert_patient_payload(self) -> UpsertPatientSchema:
        return UpsertPatientSchema(
            id=uuid.uuid4(),
            primary_identifier=self.patient_identifier,
            given_name=self.given_name,
            family_name=self.family_name,
            birth_date=self.birth_date,
            active=True,
            gender=HL7_TO_FHIR_GENDER_MAPPING[self.gender],
        )


class WebPatientAdmission(WebBaseSchema):
    bed_id: UUID = Field(..., alias="bedId")
    payload: Union[WebQuickAdmitPayload, WebEHRAdmitPayload] = Field(..., discriminator="type")
