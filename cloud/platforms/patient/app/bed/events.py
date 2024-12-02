from typing import Any, Optional

from app.bed.schemas import (
    CreateBedGroupSchema,
    CreateBedSchema,
    UpdateBedGroupSchema,
    UpdateBedSchema,
)
from app.common.event_sourcing.events import Event
from app.common.models import Bed, BedGroup


class CreateBedEvent(Event[Bed]):
    display_name: str = "Bed created"
    event_type: str = "BED_CREATED_EVENT"

    def __init__(self, username: str, payload: CreateBedSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, entity: Optional[Bed] = None) -> Bed:
        bed = Bed(
            id=self.payload.id,
            name=self.payload.name,
        )
        return bed

    def as_dict(self) -> dict[str, Any]:
        return {"id": self.payload.id, "name": self.payload.name}


class UpdateBedEvent(Event[Bed]):
    display_name: str = "Bed updated"
    event_type: str = "BED_UPDATED_EVENT"

    def __init__(self, username: str, payload: UpdateBedSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, entity: Bed) -> Bed:
        entity.name = self.payload.name
        return entity

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.payload.name}


class DeleteBedEvent(Event[Bed]):
    display_name: str = "Bed deleted"
    event_type: str = "BED_DELETED_EVENT"

    def process(self, entity: Bed) -> Bed:
        return entity


class CreateBedGroupEvent(Event[BedGroup]):
    display_name: str = "Bed group created"
    event_type: str = "BED_GROUP_CREATED_EVENT"

    def __init__(self, username: str, payload: CreateBedGroupSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, entity: Optional[Bed] = None) -> Bed:
        bed_group = BedGroup(
            id=self.payload.id,
            name=self.payload.name,
            description=self.payload.description,
            beds=[],
        )
        return bed_group

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.payload.id,
            "name": self.payload.name,
            "description": self.payload.description,
            "beds": [],
        }


class UpdateBedGroupEvent(Event[BedGroup]):
    display_name: str = "Bed group updated"
    event_type: str = "BED_GROUP_UPDATED_EVENT"

    def __init__(self, username: str, payload: UpdateBedGroupSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, entity: BedGroup) -> BedGroup:
        entity.name = self.payload.name
        entity.description = self.payload.description
        return entity

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.payload.name,
            "description": self.payload.description,
            "beds": [],
        }


class DeleteBedGroupEvent(Event[BedGroup]):
    display_name: str = "Bed group deleted"
    event_type: str = "BED_GROUP_DELETED_EVENT"

    def process(self, entity: BedGroup) -> BedGroup:
        return entity


class AssignBedToGroupEvent(Event[BedGroup]):
    display_name: str = "Bed added to group"
    event_type: str = "BED_ASSIGNED_TO_GROUP_EVENT"

    def __init__(self, username: str, bed: Bed):
        super().__init__(username)
        self.bed = bed

    def process(self, entity: BedGroup) -> BedGroup:
        entity.beds.append(self.bed)
        return entity

    def as_dict(self) -> dict[str, Any]:
        return {"bed": self.bed.as_dict()}


class RemoveBedFromGroupEvent(Event[BedGroup]):
    display_name: str = "Bed removed from group"
    event_type: str = "BED_REMOVED_FROM_GROUP_EVENT"

    def __init__(self, username: str, bed: Bed):
        super().__init__(username)
        self.bed = bed

    def process(self, entity: BedGroup) -> BedGroup:
        entity.beds.remove(self.bed)
        return entity

    def as_dict(self) -> dict[str, Any]:
        return {"bed": self.bed.as_dict()}
