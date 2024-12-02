# pylint: disable=E1102,R0801
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import Query
from pydantic import Field, StringConstraints
from typing_extensions import Annotated

from app.common.schemas import BaseSchema


class VitalRange(BaseSchema):
    id: UUID
    code: str
    alert_condition_enabled: bool
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None


class DeviceAlert(BaseSchema):
    id: UUID
    code: str
    priority: str
    created_at: datetime


class DeviceSchema(BaseSchema):
    id: UUID
    primary_identifier: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    name: str
    gateway_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    audio_pause_enabled: Optional[bool] = False
    audio_enabled: Optional[bool] = True
    subject_identifier: Optional[str] = None
    model_number: str


class DeviceResource(DeviceSchema):
    vital_ranges: List[VitalRange] = []
    alerts: List[DeviceAlert] = []


class DeviceResources(BaseSchema):
    resources: List[DeviceResource]


class CreateDeviceSchema(DeviceSchema):
    pass


class UpdateDeviceSchema(CreateDeviceSchema):
    pass


class DeleteDeviceSchema(BaseSchema):
    device_id: UUID


class AssignLocationSchema(BaseSchema):
    bed_id: Optional[UUID] = None
    device_id: UUID


class BatchAssignLocationsSchema(BaseSchema):
    associations: List[AssignLocationSchema]


class BatchUnassignLocationsSchema(BaseSchema):
    device_ids: List[UUID]


class DeviceQueryParams(BaseSchema):
    device_code: Optional[str] = None
    gateway: Optional[UUID] = None
    location_id: List[UUID] = Field(Query([]))
    is_gateway: Optional[bool] = None


class CreateDeviceAlertSchema(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    device_id: UUID
    code: str
    priority: str


class UpdateDeviceAlertSchema(CreateDeviceAlertSchema):
    pass


class CreateVitalRangeSchema(BaseSchema):
    id: UUID = Field(default_factory=uuid4)
    code: str
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None
    alert_condition_enabled: bool = True
    device_id: UUID


class VitalRangesResources(BaseSchema):
    resources: List[VitalRange]
