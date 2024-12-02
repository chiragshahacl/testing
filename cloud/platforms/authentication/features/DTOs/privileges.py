import uuid

from pydantic import BaseModel

from features.DTOs.common import BasePaginationDTO


class PrivilegeDTO(BaseModel):
    id: uuid.UUID
    name: str


class PrivilegePaginationDTO(BasePaginationDTO):
    resources: list[PrivilegeDTO]
