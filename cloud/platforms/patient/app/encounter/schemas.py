from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field

from app.common.schemas import BaseSchema
from app.device.src.device.schemas import DeviceSchema
from app.encounter.enums import EncounterStatus
from app.encounter.models import Encounter
from app.patient.schemas import PatientSchema


class EncounterSchema(BaseSchema):
    id: UUID
    subject_id: UUID
    device_id: UUID
    created_at: datetime
    status: EncounterStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class AdmissionSchema(BaseSchema):
    id: UUID
    subject: PatientSchema
    device: DeviceSchema
    created_at: datetime
    status: EncounterStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @classmethod
    def from_encounter(cls, encounter: Encounter) -> "AdmissionSchema":
        admission = None
        if encounter:
            patient_schema = PatientSchema.model_validate(encounter.subject)
            device_schema = DeviceSchema.model_validate(encounter.device)
            admission = cls.model_construct(
                id=encounter.id,
                subject=patient_schema,
                device=device_schema,
                created_at=encounter.created_at,
                status=encounter.status,
                start_time=encounter.start_time,
                end_time=encounter.end_time,
            )

        return admission


class AdmissionResource(BaseSchema):
    resource: Optional[AdmissionSchema]


class PatientAdmissionSchema(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    subject_id: UUID
    bed_id: UUID


class DismissPatientAdmissionPayload(BaseSchema):
    patient_id: UUID
