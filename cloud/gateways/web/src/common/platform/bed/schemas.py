from typing import List, Optional
from uuid import UUID

from src.common.platform.patient.schemas import PlatformEncounter, PlatformPatient
from src.common.schemas import BaseSchema


class PlatformBatchAssignBeds(BaseSchema):
    bed_ids: List[UUID]
    group_id: UUID


class PlatformBed(BaseSchema):
    id: UUID
    name: str
    patient: Optional[PlatformPatient] = None
    encounter: Optional[PlatformEncounter] = None


class PlatformCreateBedBatch(BaseSchema):
    beds: List[PlatformBed]


class PlatformBedResources(BaseSchema):
    resources: List[PlatformBed]


class PlatformUpdateBedBatch(BaseSchema):
    beds: List[PlatformBed]


class PlatformDeleteBedBatch(BaseSchema):
    bed_ids: List[UUID]
