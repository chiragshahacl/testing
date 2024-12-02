from typing import List, Optional
from uuid import UUID

from src.common.schemas import BaseSchema


class PlatformBedGroupBed(BaseSchema):
    id: UUID
    name: str


class PlatformBedGroup(BaseSchema):
    id: UUID
    name: str
    description: Optional[str] = None
    beds: List[PlatformBedGroupBed]


class PlatformBedGroupResources(BaseSchema):
    resources: List[PlatformBedGroup]


class PlatformDeleteBedGroup(BaseSchema):
    group_ids: List[UUID]


class PlatformBedGroupBatchCreate(BaseSchema):
    groups: List[PlatformBedGroup]


class PlatformBedGroupBatchUpdate(BaseSchema):
    groups: List[PlatformBedGroup]


class PlatformAssignBeds(BaseSchema):
    group_id: UUID
    bed_ids: List[UUID]


class PlatformBatchAssignBeds(BaseSchema):
    resources: List[PlatformAssignBeds]
