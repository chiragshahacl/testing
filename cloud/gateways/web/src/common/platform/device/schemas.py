from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.common.schemas import BaseSchema


class PlatformAssignBed(BaseSchema):
    bed_id: UUID
    device_id: UUID


class PlatformBatchAssignBeds(BaseSchema):
    associations: List[PlatformAssignBed]


class PlatformBatchUnassignBeds(BaseSchema):
    device_ids: List[UUID]


class PlatformDeviceQueryParams(BaseSchema):
    gateway: Optional[UUID] = None
    location_id: Optional[list[UUID]] = None
    is_gateway: Optional[bool] = None
    device_code: Optional[str] = None


# pylint: disable=duplicate-code
class PlatformDeviceRange(BaseSchema):
    id: UUID
    code: str
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None
    alert_condition_enabled: bool = True


class PlatformDeviceAlert(BaseSchema):
    id: UUID
    code: str
    priority: str
    created_at: datetime


class PlatformDeviceRangesResources(BaseSchema):
    resources: List[PlatformDeviceRange]


# pylint: disable=duplicate-code
class PlatformDevice(BaseSchema, protected_namespaces=()):
    id: UUID
    primary_identifier: str
    name: str
    location_id: Optional[UUID] = None
    gateway_id: Optional[UUID] = None
    audio_pause_enabled: bool
    audio_enabled: bool
    model_number: str
    vital_ranges: List[PlatformDeviceRange] = []
    alerts: List[PlatformDeviceAlert] = []


class PlatformDeviceResources(BaseSchema):
    resources: List[PlatformDevice]


class PlatformCreateDevice(PlatformDevice):
    pass


class PlatformUpdateDevice(PlatformDevice):
    pass


class PlatformDeviceTechnicalAlert(BaseSchema):
    code: str
    start_determination_time: datetime
    end_determination_time: datetime
    value_text: str
    device_primary_identifier: str
    device_code: str
