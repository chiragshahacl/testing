import uuid
from typing import List, Optional
from uuid import UUID

from pydantic import Field
from typing_extensions import Annotated

from src.common.platform.bed import schemas as bed_platform_schemas
from src.common.schemas import WebBaseSchema
from src.patient import schemas as web_patient_schemas


class WebBed(WebBaseSchema):
    id: UUID
    name: str
    patient: Optional[web_patient_schemas.WebPatient] = None
    encounter: Optional[web_patient_schemas.WebEncounter] = None

    @classmethod
    def from_platform(cls, payload: bed_platform_schemas.PlatformBed) -> "WebBed":
        patient_schema = None
        encounter_schema = None
        if payload.patient:
            patient_schema = web_patient_schemas.WebPatient.from_platform(payload.patient)
        if payload.encounter:
            encounter_schema = web_patient_schemas.WebEncounter.from_platform(payload.encounter)
        return cls.model_construct(
            id=payload.id, name=payload.name, patient=patient_schema, encounter=encounter_schema
        )


class WebCreateBed(WebBaseSchema):
    name: str

    def to_platform(self) -> bed_platform_schemas.PlatformBed:
        return bed_platform_schemas.PlatformBed.model_construct(
            id=uuid.uuid4(),
            name=self.name,
        )


class WebBedResources(WebBaseSchema):
    resources: List[WebBed]

    @classmethod
    def from_platform(cls, payload: bed_platform_schemas.PlatformBedResources) -> "WebBedResources":
        return cls.model_construct(
            resources=[WebBed.from_platform(bed) for bed in payload.resources],
        )


class WebBatchCreateBeds(WebBaseSchema):
    resources: List[WebCreateBed]

    def to_platform(self) -> bed_platform_schemas.PlatformCreateBedBatch:
        return bed_platform_schemas.PlatformCreateBedBatch.model_construct(
            beds=[bed.to_platform() for bed in self.resources]
        )


class WebBatchDeleteBeds(WebBaseSchema):
    bed_ids: Annotated[List[UUID], Field(min_length=1)]

    def to_platform(self) -> bed_platform_schemas.PlatformDeleteBedBatch:
        return bed_platform_schemas.PlatformDeleteBedBatch.model_construct(bed_ids=self.bed_ids)


class WebUpdateOrCreateBed(WebBaseSchema):
    id: Optional[UUID] = None
    name: str

    def to_platform_bed(self) -> bed_platform_schemas.PlatformBed:
        return bed_platform_schemas.PlatformBed(
            id=self.id or uuid.uuid4(),
            name=self.name,
        )


class WebBatchCreateOrUpdateBeds(WebBaseSchema):
    resources: List[WebUpdateOrCreateBed]

    @staticmethod
    def to_platform_batch_create(
        resources: List[WebUpdateOrCreateBed],
    ) -> bed_platform_schemas.PlatformCreateBedBatch:
        return bed_platform_schemas.PlatformCreateBedBatch.model_construct(
            beds=[bed.to_platform_bed() for bed in resources]
        )

    @staticmethod
    def to_platform_batch_update(
        resources: List[WebUpdateOrCreateBed],
    ) -> bed_platform_schemas.PlatformUpdateBedBatch:
        return bed_platform_schemas.PlatformUpdateBedBatch.model_construct(
            beds=[bed.to_platform_bed() for bed in resources]
        )
