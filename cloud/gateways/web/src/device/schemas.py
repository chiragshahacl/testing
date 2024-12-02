from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import Field

from src.common.platform.device import schemas as device_platform_schemas
from src.common.schemas import BaseSchema, WebBaseSchema


class WebDeviceQueryParams(WebBaseSchema):
    bed_ids: Optional[list[UUID]] = None
    gateway_id: Optional[UUID] = None
    is_gateway: Optional[bool] = None
    device_code: Optional[str] = None
    bed_group: Optional[UUID] = None

    def to_platform(self) -> device_platform_schemas.PlatformDeviceQueryParams:
        return device_platform_schemas.PlatformDeviceQueryParams.model_construct(
            gateway=self.gateway_id,
            location_id=self.bed_ids,
            is_gateway=self.is_gateway,
            device_code=self.device_code,
        )


class WebAssignBedSchema(WebBaseSchema):
    bed_id: Optional[UUID] = None
    device_id: UUID

    def to_platform(self):
        return device_platform_schemas.PlatformAssignBed.model_construct(
            bed_id=self.bed_id, device_id=self.device_id
        )


class WebBatchAssignBedsSchema(WebBaseSchema):
    associations: List[WebAssignBedSchema]

    def to_platform(self) -> device_platform_schemas.PlatformBatchAssignBeds:
        return device_platform_schemas.PlatformBatchAssignBeds.model_construct(
            associations=[
                association.to_platform()
                for association in self.associations
                if association is not None
            ]
        )


class WebCreateOrUpdateDevice(WebBaseSchema):
    id: UUID
    name: str
    primary_identifier: str
    gateway_id: Optional[UUID] = None
    device_code: str

    def to_platform_create(self) -> device_platform_schemas.PlatformCreateDevice:
        return device_platform_schemas.PlatformCreateDevice.model_construct(
            id=self.id,
            name=self.name,
            primary_identifier=self.primary_identifier,
            gateway_id=self.gateway_id,
            model_number=self.device_code,
        )

    def to_platform_update(self) -> device_platform_schemas.PlatformUpdateDevice:
        return device_platform_schemas.PlatformUpdateDevice.model_construct(
            id=self.id,
            name=self.name,
            primary_identifier=self.primary_identifier,
            gateway_id=self.gateway_id,
            model_number=self.device_code,
        )


class WebDeviceRange(WebBaseSchema):
    id: UUID
    code: str
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None
    alert_condition_enabled: bool

    @classmethod
    def from_platform(
        cls, payload: device_platform_schemas.PlatformDeviceRange
    ) -> "WebDeviceRange":
        return cls.model_construct(
            id=payload.id,
            code=payload.code,
            upper_limit=payload.upper_limit,
            lower_limit=payload.lower_limit,
            alert_condition_enabled=payload.alert_condition_enabled,
        )


class WebDeviceAlert(WebBaseSchema):
    id: UUID
    code: str
    priority: str
    created_at: datetime = Field(alias="createdAt")

    @classmethod
    def from_platform(
        cls, payload: device_platform_schemas.PlatformDeviceAlert
    ) -> "WebDeviceAlert":
        return cls.model_construct(
            id=payload.id,
            code=payload.code,
            priority=payload.priority,
            created_at=payload.created_at,
        )


class WebDeviceRangesResources(WebBaseSchema):
    resources: List[WebDeviceRange]

    @classmethod
    def from_platform(
        cls, payload: device_platform_schemas.PlatformDeviceRangesResources
    ) -> "WebDeviceRangesResources":
        return cls.model_construct(
            resources=[
                WebDeviceRange.from_platform(device_range) for device_range in payload.resources
            ],
        )


class DeviceConfig(BaseSchema):
    audio_pause_enabled: bool
    audio_enabled: bool


# pylint: disable=duplicate-code
class WebDevice(WebBaseSchema):
    id: UUID
    primary_identifier: str
    name: str
    location_id: Optional[UUID] = None
    gateway_id: Optional[UUID] = None
    config: DeviceConfig
    device_code: str
    vital_ranges: List[WebDeviceRange] = []
    alerts: List[WebDeviceAlert] = []

    @classmethod
    def from_platform(cls, payload: device_platform_schemas.PlatformDevice) -> "WebDevice":
        return cls.model_construct(
            id=payload.id,
            primary_identifier=payload.primary_identifier,
            name=payload.name,
            location_id=payload.location_id,
            gateway_id=payload.gateway_id,
            device_code=payload.model_number,
            vital_ranges=payload.vital_ranges,
            alerts=[WebDeviceAlert.from_platform(alert) for alert in payload.alerts],
            config=DeviceConfig(
                audio_pause_enabled=payload.audio_pause_enabled,
                audio_enabled=payload.audio_enabled,
            ),
        )


class WebDeviceResources(WebBaseSchema):
    resources: List[WebDevice]

    @classmethod
    def from_platform(
        cls, payload: device_platform_schemas.PlatformDeviceResources
    ) -> "WebDeviceResources":
        return cls.model_construct(
            resources=[WebDevice.from_platform(device) for device in payload.resources],
        )


class WebDeviceCommandSchema(WebBaseSchema):
    command_name: Literal["ALARM_VALIDATION_ON", "ALARM_VALIDATION_OFF"]
    pm_identifier: str
    params: Dict[str, Any] = {}


class DeviceCommandSchema(WebBaseSchema):
    request_id: UUID
    command_name: str
    pm_id: UUID
    params: Dict[str, Any] = {}

    @classmethod
    def from_payload(cls, payload: WebDeviceCommandSchema, pm_id: UUID) -> "DeviceCommandSchema":
        return cls.model_construct(
            command_name=payload.command_name, pm_id=pm_id, params=payload.params
        )

    def as_dict(self):
        return {
            "command_name": self.command_name,
            "id": self.pm_id,
            "pm_id": self.pm_id,
            "params": self.params,
        }
