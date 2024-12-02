from typing import List
from uuid import UUID

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request

from app.bed.events import (
    AssignBedToGroupEvent,
    CreateBedEvent,
    CreateBedGroupEvent,
    DeleteBedEvent,
    DeleteBedGroupEvent,
    RemoveBedFromGroupEvent,
    UpdateBedEvent,
    UpdateBedGroupEvent,
)
from app.bed.repositories import ReadBedRepository
from app.bed.schemas import (
    BedGroupResourcesSchema,
    BedGroupSchema,
    BedResourcesSchema,
    BedSchema,
    CreateBedGroupSchema,
    CreateBedSchema,
    UpdateBedGroupSchema,
    UpdateBedSchema,
)
from app.common.exceptions import BaseValidationException
from app.common.schemas import ErrorSchema
from app.patient.repository import ReadPatientRepository
from app.patient.stream import BedEventStream, BedGroupEventStream, PatientEventStream
from app.settings import config


class BedNameInUse(BaseValidationException):
    def __init__(self) -> None:
        self.error = ErrorSchema(
            loc=["body", "name"],
            msg="Name already in use",
            type="value_error.already_in_use",
        )


class BedAssignedToGroup(BaseValidationException):
    def __init__(self) -> None:
        self.error = ErrorSchema(
            loc=["body", "group_id"],
            msg="Bed already assigned to a group",
            type="value_error.already_in_use",
        )


class BedGroupNameInUse(BaseValidationException):
    def __init__(self) -> None:
        self.error = ErrorSchema(
            loc=["body", "name"],
            msg="Bed group name already exists. Change or enter a new one.",
            type="value_error.already_in_use",
        )


class TooManyBeds(BaseValidationException):
    def __init__(self):
        self.error = ErrorSchema(
            loc=["body"],
            msg=(
                "You have reached the maximum number "
                f"of beds for the system ({config.MAX_BEDS})."
            ),
            type="value_error.too_many_beds",
        )


class BedNotFound(BaseValidationException):
    def __init__(self):
        self.error = ErrorSchema(
            loc=["body"],
            msg="Bed not found.",
            type="value_error.not_found",
        )


class BedGroupNotFound(BaseValidationException):
    def __init__(self):
        self.error = ErrorSchema(
            loc=["body", "group_id"],
            msg="Bed group not found.",
            type="value_error.not_found",
        )


class BedGroupIsFull(BaseValidationException):
    def __init__(self):
        self.error = ErrorSchema(
            loc=["body", "group_id"],
            msg=(
                "You have reached the maximum number "
                f"of beds for the system ({config.MAX_BEDS})."
            ),
            type="value_error.bed_group_full",
        )


class PatientNotFound(BaseValidationException):
    def __init__(self):
        self.error = ErrorSchema(
            loc=["body"],
            msg="Patient with provided id not found",
            type="value_error.patient_not_found",
        )


class BedService:
    def __init__(
        self,
        request: Request,
        read_bed_repository: ReadBedRepository = Depends(),
        bed_event_stream: BedEventStream = Depends(),
        bed_group_event_stream: BedGroupEventStream = Depends(),
        read_patient_repository: ReadPatientRepository = Depends(),
        patient_event_stream: PatientEventStream = Depends(),
    ):  # pylint: disable=too-many-arguments
        self.username = request.state.username
        self.read_bed_repository = read_bed_repository
        self.bed_event_stream = bed_event_stream
        self.bed_group_event_stream = bed_group_event_stream
        self.read_patient_repository = read_patient_repository
        self.patient_event_stream = patient_event_stream

    async def batch_create_beds(self, beds: List[CreateBedSchema]) -> BedResourcesSchema:
        found_beds = await self.read_bed_repository.get_beds(lock=True)
        if len(found_beds) + len(beds) > config.MAX_BEDS:
            raise TooManyBeds
        try:
            events_and_entities = [(CreateBedEvent(self.username, bed), None) for bed in beds]
            beds = await self.bed_event_stream.batch_add(events_and_entities)
        except IntegrityError as exc:
            if "ix_unique_bed_name" in exc.args[0]:
                raise BedNameInUse from exc
            raise exc
        return BedResourcesSchema.model_construct(
            resources=[BedSchema.model_validate(bed) for bed in beds]
        )

    async def batch_update_beds(self, beds: List[UpdateBedSchema]) -> BedResourcesSchema:
        found_beds = await self.read_bed_repository.get_beds(
            lock=True, with_ids=[b.id for b in beds]
        )
        if len(found_beds) != len(beds):
            raise BedNotFound

        try:
            found_beds_by_id = {b.id: b for b in found_beds}
            processed_beds = await self.bed_event_stream.batch_add(
                [(UpdateBedEvent(self.username, bed), found_beds_by_id[bed.id]) for bed in beds]
            )
        except IntegrityError as exc:
            if "ix_unique_bed_name" in exc.args[0]:
                raise BedNameInUse from exc
            raise exc
        return BedResourcesSchema.model_construct(
            resources=[BedSchema.model_validate(bed) for bed in processed_beds]
        )

    async def create_bed(self, payload: CreateBedSchema) -> BedSchema:
        found_beds = await self.read_bed_repository.get_beds(lock=True)
        if len(found_beds) >= config.MAX_BEDS:
            raise TooManyBeds
        try:
            event = CreateBedEvent(self.username, payload)
            bed = await self.bed_event_stream.add(event, None)
        except IntegrityError as exc:
            if "ix_unique_bed_name" in exc.args[0]:
                raise BedNameInUse from exc
            raise exc
        return bed

    async def delete_bed(self, bed_id: UUID) -> None:
        bed = await self.read_bed_repository.get_bed(bed_id, lock=True)

        if not bed:
            raise BedNotFound

        if bed.groups:
            raise BedAssignedToGroup

        event = DeleteBedEvent(self.username)
        await self.bed_event_stream.delete(event, bed)

    async def batch_delete_beds(self, bed_ids: List[UUID]) -> None:
        beds = await self.read_bed_repository.get_beds(bed_ids)
        events = [(DeleteBedEvent(username=self.username), bed) for bed in beds]
        await self.bed_event_stream.batch_delete(events)

    async def batch_create_bed_groups(
        self, groups: List[CreateBedGroupSchema]
    ) -> BedGroupResourcesSchema:
        try:
            events_and_entities = [
                (CreateBedGroupEvent(self.username, group), None) for group in groups
            ]
            groups = await self.bed_group_event_stream.batch_add(events_and_entities)
        except IntegrityError as exc:
            if "ix_unique_bed_group_name" in exc.args[0]:
                raise BedGroupNameInUse from exc
            raise exc
        return BedGroupResourcesSchema.model_construct(
            resources=[BedGroupSchema.model_validate(group) for group in groups]
        )

    async def batch_update_bed_groups(
        self, groups: List[UpdateBedGroupSchema]
    ) -> BedGroupResourcesSchema:
        found_bed_groups = await self.read_bed_repository.get_bed_groups(
            lock=True, with_ids=[group.id for group in groups]
        )
        if len(found_bed_groups) != len(groups):
            raise BedGroupNotFound

        try:
            found_bed_groups_by_id = {group.id: group for group in found_bed_groups}
            processed_groups = await self.bed_group_event_stream.batch_add(
                [
                    (
                        UpdateBedGroupEvent(self.username, group),
                        found_bed_groups_by_id[group.id],
                    )
                    for group in groups
                ]
            )
        except IntegrityError as exc:
            if "ix_unique_bed_group_name" in exc.args[0]:
                raise BedGroupNameInUse from exc
            raise exc
        return BedGroupResourcesSchema.model_construct(
            resources=[BedGroupSchema.model_validate(group) for group in processed_groups]
        )

    async def create_bed_group(self, group: CreateBedGroupSchema) -> BedGroupSchema:
        try:
            event = CreateBedGroupEvent(self.username, group)
            group = await self.bed_group_event_stream.add(event, None)
        except IntegrityError as exc:
            if "ix_unique_bed_group_name" in exc.args[0]:
                raise BedGroupNameInUse from exc
            raise exc
        return BedGroupSchema.model_validate(group)

    async def batch_delete_bed_groups(self, group_ids: List[UUID]) -> None:
        bed_groups = await self.read_bed_repository.get_bed_groups(with_ids=group_ids)
        events = [
            (DeleteBedGroupEvent(username=self.username), bed_group) for bed_group in bed_groups
        ]
        await self.bed_group_event_stream.batch_delete(events)

    async def batch_assign_beds(self, bed_group_id: UUID, bed_ids: List[UUID]) -> None:
        bed_group = await self.read_bed_repository.get_bed_group_by_id(bed_group_id, lock=True)

        if not bed_group:
            raise BedGroupNotFound

        if len(bed_ids) > config.MAX_BEDS_PER_GROUP:
            raise BedGroupIsFull

        found_beds = await self.read_bed_repository.get_beds(with_ids=bed_ids)
        if not found_beds or len(bed_ids) != len(found_beds):
            raise BedNotFound

        remove_events = []
        for bed in bed_group.beds:
            remove_events.append((RemoveBedFromGroupEvent(self.username, bed), bed_group))

        await self.bed_group_event_stream.batch_add(remove_events)

        assign_events = []
        for bed in found_beds:
            assign_events.append((AssignBedToGroupEvent(self.username, bed), bed_group))

        await self.bed_group_event_stream.batch_add(assign_events)

    async def get_beds(self) -> BedResourcesSchema:
        beds_with_patients_and_encounters = await self.read_bed_repository.get_beds_with_patients()
        return BedResourcesSchema.model_construct(
            resources=[
                BedSchema.from_bed(bed, patient, encounter)
                for bed, patient, encounter in beds_with_patients_and_encounters
            ]
        )

    async def get_bed_groups(self) -> BedGroupResourcesSchema:
        groups = await self.read_bed_repository.get_bed_groups()
        return BedGroupResourcesSchema.model_construct(
            resources=[BedGroupSchema.model_validate(bg) for bg in groups]
        )

    async def get_group_beds(self, group_id: UUID) -> BedResourcesSchema:
        beds_with_patients_and_encounter = await self.read_bed_repository.get_beds_for_group(
            group_id
        )
        return BedResourcesSchema.model_construct(
            resources=[
                BedSchema.from_bed(bed, patient, encounter)
                for bed, patient, encounter in beds_with_patients_and_encounter
            ]
        )

    async def add_bed_to_group(self, group_id: UUID, bed_id: UUID) -> None:
        bed_group = await self.read_bed_repository.get_bed_group_by_id(group_id, lock=True)

        if not bed_group:
            raise BedGroupNotFound

        if len(bed_group.beds) + 1 > config.MAX_BEDS_PER_GROUP:
            raise BedGroupIsFull

        found_bed = await self.read_bed_repository.get_bed(bed_id)

        if not found_bed:
            raise BedNotFound

        event = AssignBedToGroupEvent(self.username, found_bed)
        await self.bed_group_event_stream.add(event, bed_group)

    async def remove_bed_from_group(self, group_id: UUID, bed_id: UUID) -> None:
        bed_group = await self.read_bed_repository.get_bed_group_by_id(group_id, lock=True)
        bed = await self.read_bed_repository.get_bed(bed_id)

        if not bed_group:
            raise BedGroupNotFound

        if not bed:
            raise BedNotFound
        event = RemoveBedFromGroupEvent(self.username, bed)
        await self.bed_group_event_stream.add(event, bed_group)

    async def delete_bed_group(self, group_id: UUID) -> None:
        bed_group = await self.read_bed_repository.get_bed_group_by_id(group_id, lock=True)

        if not bed_group:
            raise BedGroupNotFound

        event = DeleteBedGroupEvent(self.username)
        await self.bed_group_event_stream.delete(event, bed_group)
