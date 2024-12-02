from typing import List

from src.common.schemas import BaseSchema


class PlatformConfig(BaseSchema):
    key: str
    value: str


class PlatformConfigResources(BaseSchema):
    resources: List[PlatformConfig]


class PlatformUpdateConfigBatch(BaseSchema):
    configs: List[PlatformConfig]
