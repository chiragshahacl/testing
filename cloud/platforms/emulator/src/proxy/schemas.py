from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class DeviceSchema(BaseModel):
    id: UUID
    primary_identifier: str
    name: str
    gateway_id: Optional[UUID]
    model_number: str


class DeleteDeviceSchema(BaseModel):
    device_id: UUID


class BatchDeleteDeviceSchema(BaseModel):
    device_ids: List[DeleteDeviceSchema]
