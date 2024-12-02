from typing import List, Optional
from uuid import UUID

from pydantic import Field, StringConstraints
from typing_extensions import Annotated

from app.common.models import Bed, Patient
from app.common.schemas import BaseSchema
from app.encounter.models import Encounter
from app.encounter.schemas import EncounterSchema
from app.patient.schemas import PatientSchema


class CreateBedSchema(BaseSchema):
    id: UUID
    name: Annotated[str, StringConstraints(min_length=1, max_length=50)]


class DeleteBedSchema(BaseSchema):
    bed_id: UUID


class UpdateBedSchema(BaseSchema):
    id: UUID
    name: Annotated[str, StringConstraints(min_length=1, max_length=50)]


class BatchDeleteBedSchema(BaseSchema):
    bed_ids: Annotated[List[UUID], Field(min_length=1)]


class BatchCreateBedsSchema(BaseSchema):
    beds: List[CreateBedSchema]


class BatchUpdateBedsSchema(BaseSchema):
    beds: List[UpdateBedSchema]


class BedSchema(BaseSchema):
    id: UUID
    name: str
    patient: Optional[PatientSchema] = None
    encounter: Optional[EncounterSchema] = None

    @classmethod
    def from_bed(
        cls, bed: Bed, patient: Optional[Patient], encounter: Optional[Encounter]
    ) -> "BedSchema":
        patient_schema = None
        encounter_schema = None
        if patient:
            patient_schema = PatientSchema.model_validate(patient)
        if encounter:
            encounter_schema = EncounterSchema.model_validate(encounter)
        return cls.model_construct(
            id=bed.id, name=bed.name, patient=patient_schema, encounter=encounter_schema
        )


class BedResourcesSchema(BaseSchema):
    resources: List[BedSchema]


class BedGroupBedSchema(BaseSchema):
    id: UUID
    name: str


class BedGroupSchema(BaseSchema):
    id: UUID
    name: Annotated[str, StringConstraints(min_length=1, max_length=50)]
    description: Optional[Annotated[str, StringConstraints(min_length=1, max_length=100)]] = None
    beds: List[BedGroupBedSchema]


class UpdateBedGroupSchema(BaseSchema):
    id: UUID
    name: Annotated[str, StringConstraints(min_length=1, max_length=50)]
    description: Optional[Annotated[str, StringConstraints(min_length=1, max_length=100)]] = None


class CreateBedGroupSchema(BaseSchema):
    id: UUID
    name: Annotated[str, StringConstraints(min_length=1, max_length=50)]
    description: Optional[Annotated[str, StringConstraints(min_length=1, max_length=100)]] = None


class BatchCreateBedGroupsSchema(BaseSchema):
    groups: List[CreateBedGroupSchema]


class BatchUpdateBedGroupsSchema(BaseSchema):
    groups: List[UpdateBedGroupSchema]


class BatchDeleteBedGroupsSchema(BaseSchema):
    group_ids: Annotated[List[UUID], Field(min_length=1)]


class BedGroupResourcesSchema(BaseSchema):
    resources: List[BedGroupSchema]


class GroupBedAssignmentSchema(BaseSchema):
    group_id: UUID
    bed_ids: List[UUID]


class BatchAssignBedsSchema(BaseSchema):
    resources: List[GroupBedAssignmentSchema]


class AddBedToGroupSchema(BaseSchema):
    bed_id: UUID
    group_id: UUID


class RemoveBedFromGroupSchema(BaseSchema):
    bed_id: UUID
    group_id: UUID


class DeleteBedGroupSchema(BaseSchema):
    group_id: UUID
