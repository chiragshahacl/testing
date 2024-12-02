from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from common_schemas import SecretDate, SecretString
from fastapi import Query
from pydantic import Field, StringConstraints
from typing_extensions import Annotated

from app.common.schemas import BaseSchema
from app.patient.enums import GenderEnum


class CreatePatientSchema(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    primary_identifier: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    active: bool
    given_name: SecretString = Field(min_length=1, max_length=255)
    family_name: SecretString
    gender: GenderEnum
    birth_date: Optional[SecretDate] = None


class UpdatePatientSchema(CreatePatientSchema):
    pass


class DeletePatientSchema(BaseSchema):
    id: UUID


class PatientSchema(BaseSchema):
    id: UUID
    primary_identifier: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    active: bool
    given_name: SecretString = Field(min_length=1, max_length=255)
    family_name: str
    gender: GenderEnum
    birth_date: Optional[SecretDate] = None


class PatientQueryParams(BaseSchema):
    identifier: Optional[str] = None


class PatientObservationsQueryParams(BaseSchema):
    is_alert: Optional[bool] = Field(None, alias="isAlert")
    patient_ids: List[str] = Field(Query(alias="patientIds"))


class PatientResources(BaseSchema):
    resources: List[PatientSchema]


class PatientCount(BaseSchema):
    total: int


class CreateObservationSchema(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    category: str = Field(default="vital-signs")
    code: str
    subject_id: UUID
    effective_dt: datetime
    value_number: Optional[Decimal] = Field(None)
    value_text: Optional[str] = Field(None)
    device_code: str
    device_primary_identifier: str
    is_alert: bool


class PatientObservation(BaseSchema):
    id: UUID
    category: str
    code: str
    subject_id: UUID
    effective_dt: datetime
    value_number: Optional[Decimal] = None
    value_text: Optional[str] = None
    device_primary_identifier: Optional[str] = None
    device_code: Optional[str] = None


class PatientObservationResources(BaseSchema):
    resources: List[PatientObservation]


class SessionPhysiologicalAlert(BaseSchema):
    code: str
    start_determination_time: datetime
    end_determination_time: datetime
    value_text: str
    device_primary_identifier: str
    device_code: str
    trigger_lower_limit: Optional[float] = None
    trigger_upper_limit: Optional[float] = None
