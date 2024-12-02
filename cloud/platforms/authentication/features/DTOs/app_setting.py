import uuid

from pydantic import BaseModel

from features.DTOs.common import BasePaginationDTO


class AppSettingDTO(BaseModel):
    key: str
    value: str


class AppSettingPaginationDTO(BasePaginationDTO):
    resources: list[AppSettingDTO]
