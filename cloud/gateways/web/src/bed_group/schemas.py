import datetime
import uuid
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import Field, StringConstraints
from pydantic.types import Decimal
from typing_extensions import Annotated

from src.common.platform.bed import schemas as bed_platform_schemas
from src.common.platform.bed_group import schemas as bed_group_platform_schemas
from src.common.platform.patient import schemas as patient_platform_schemas
from src.common.schemas import WebBaseSchema
from src.patient.schemas import WebPatient


class WebBedGroupBed(WebBaseSchema):
    id: UUID
    name: str

    @classmethod
    def from_platform(cls, payload: bed_platform_schemas.PlatformBed) -> "WebBedGroupBed":
        return cls.model_construct(id=payload.id, name=payload.name)


class WebBedGroup(WebBaseSchema):
    id: UUID
    name: Annotated[str, StringConstraints(min_length=1, max_length=50)]
    description: Optional[Annotated[str, StringConstraints(min_length=1, max_length=100)]] = None
    beds: List[WebBedGroupBed]

    def to_platform(self):
        bed_group_platform_schemas.PlatformBedGroup.model_construct(
            id=self.id, name=self.name, description=self.description
        )

    @classmethod
    def from_platform(cls, payload: bed_group_platform_schemas.PlatformBedGroup) -> "WebBedGroup":
        return cls.model_construct(
            id=payload.id,
            name=payload.name,
            description=payload.description,
            beds=[WebBedGroupBed.from_platform(bed) for bed in payload.beds],
        )


class WebBedGroupResources(WebBaseSchema):
    resources: List[WebBedGroup]

    def to_platform(self) -> bed_group_platform_schemas.PlatformBedGroupResources:
        return bed_group_platform_schemas.PlatformBedGroupResources.model_construct(
            resources=[bed_group.to_platform() for bed_group in self.resources],
        )

    @classmethod
    def from_platform(
        cls, payload: bed_group_platform_schemas.PlatformBedGroupResources
    ) -> "WebBedGroupResources":
        return cls.model_construct(
            resources=[WebBedGroup.from_platform(bed_group) for bed_group in payload.resources],
        )


class WebBedGroupBatchDelete(WebBaseSchema):
    group_ids: Annotated[List[UUID], Field(min_length=1)]

    def to_platform(self) -> bed_group_platform_schemas.PlatformDeleteBedGroup:
        return bed_group_platform_schemas.PlatformDeleteBedGroup.model_construct(
            group_ids=self.group_ids,
        )


class WebBedGroupCreate(WebBaseSchema):
    name: Annotated[str, StringConstraints(min_length=1, max_length=50)]
    description: Optional[Annotated[str, StringConstraints(min_length=1, max_length=50)]] = None

    def to_platform(self):
        return bed_group_platform_schemas.PlatformBedGroup.model_construct(
            name=self.name, description=self.description, id=uuid4()
        )

    @classmethod
    def from_platform(
        cls, payload: bed_group_platform_schemas.PlatformBedGroup
    ) -> "WebBedGroupCreate":
        return cls.model_construct(
            name=payload.name,
            description=payload.description,
        )


class WebBedGroupCreateResources(WebBaseSchema):
    resources: List[WebBedGroupCreate]

    def to_platform(self) -> bed_group_platform_schemas.PlatformBedGroupBatchCreate:
        return bed_group_platform_schemas.PlatformBedGroupBatchCreate.model_construct(
            groups=[bed_group.to_platform() for bed_group in self.resources],
        )


class WebAssignBedsToGroup(WebBaseSchema):
    bed_ids: List[UUID]


class WebAssignBeds(WebBaseSchema):
    group_id: UUID
    bed_ids: List[UUID]

    def to_platform(self):
        return bed_group_platform_schemas.PlatformAssignBeds.model_construct(
            group_id=self.group_id, bed_ids=self.bed_ids
        )


class WebBatchAssignBeds(WebBaseSchema):
    resources: List[WebAssignBeds]

    def to_platform(self) -> bed_group_platform_schemas.PlatformBatchAssignBeds:
        return bed_group_platform_schemas.PlatformBatchAssignBeds.model_construct(
            resources=[assignment.to_platform() for assignment in self.resources]
        )


class WebCreateOrUpdateBedGroup(WebBaseSchema):
    id: Optional[UUID] = None
    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    description: Optional[Annotated[str, StringConstraints(min_length=1, max_length=100)]] = None

    def to_platform_bed_group(self) -> bed_group_platform_schemas.PlatformBedGroup:
        return bed_group_platform_schemas.PlatformBedGroup.model_construct(
            id=uuid.uuid4() if not self.id else self.id,
            name=self.name,
            description=self.description,
        )


class WebBatchCreateOrUpdateBedGroup(WebBaseSchema):
    resources: List[WebCreateOrUpdateBedGroup]

    @classmethod
    def to_platform_batch_create(cls, bed_groups_to_create: List[WebCreateOrUpdateBedGroup]):
        return bed_group_platform_schemas.PlatformBedGroupBatchCreate.model_construct(
            groups=[bed_group.to_platform_bed_group() for bed_group in bed_groups_to_create]
        )

    @classmethod
    def to_platform_batch_update(cls, bed_groups_to_update: List[WebCreateOrUpdateBedGroup]):
        return bed_group_platform_schemas.PlatformBedGroupBatchUpdate.model_construct(
            groups=[bed_group.to_platform_bed_group() for bed_group in bed_groups_to_update]
        )


class WebAlert(WebBaseSchema):
    id: UUID
    category: str
    code: str
    effective_dt: datetime.datetime = Field(alias="effectiveDt")
    value_number: Optional[Decimal] = Field(alias="valueNumber", default=None)
    value_text: Optional[str] = Field(alias="valueText", default=None)
    device_primary_identifier: Optional[str] = Field(alias="devicePrimaryIdentifier", default=None)
    device_code: Optional[str] = Field(alias="deviceCode", default=None)

    @classmethod
    def from_platform(
        cls, payload: patient_platform_schemas.PlatformPatientObservation
    ) -> "WebAlert":
        return cls.model_construct(
            id=payload.id,
            category=payload.category,
            code=payload.code,
            effective_dt=payload.effective_dt,
            value_number=payload.value_number,
            value_text=payload.value_text,
            device_primary_identifier=payload.device_primary_identifier,
            device_code=payload.device_code,
        )


class WebPatientAlert(WebBaseSchema):
    patient_id: UUID = Field(alias="patientId")
    primary_identifier: str = Field(alias="primaryIdentifier")
    alerts: List[WebAlert]


class WebBedGroupAlertResources(WebBaseSchema):
    resources: List[WebPatientAlert]

    @staticmethod
    def _get_grouped_alerts(
        resources: List[patient_platform_schemas.PlatformPatientObservation],
    ) -> Dict[str, List[WebAlert]]:
        observations_by_patient_id = {}
        for obs in resources:
            current = observations_by_patient_id.get(obs.subject_id, [])
            current.append(WebAlert.from_platform(obs))
            observations_by_patient_id[obs.subject_id] = current
        return observations_by_patient_id

    @classmethod
    def from_platform(
        cls,
        resources: List[patient_platform_schemas.PlatformPatientObservation],
        patients_by_id: Dict[str, WebPatient],
    ) -> "WebBedGroupAlertResources":
        grouped_alerts_by_patient_id = cls._get_grouped_alerts(resources)
        return cls.model_construct(
            resources=[
                WebPatientAlert.model_construct(
                    patient_id=patient_id,
                    primary_identifier=patients_by_id[patient_id].primary_identifier,
                    alerts=alerts,
                )
                for patient_id, alerts in grouped_alerts_by_patient_id.items()
            ]
        )
