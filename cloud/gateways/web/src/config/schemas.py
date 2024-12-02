import re
from typing import List

from common_schemas import SecretString
from pydantic import BeforeValidator, conint
from typing_extensions import Annotated

from src.common.platform.config import schemas as config_platform_schemas
from src.common.schemas import WebBaseSchema


class WebConfig(WebBaseSchema):
    key: str
    value: str

    @classmethod
    def from_platform(cls, payload: config_platform_schemas.PlatformConfig) -> "WebConfig":
        return cls.model_construct(
            key=payload.key,
            value=payload.value,
        )


class WebConfigResources(WebBaseSchema):
    resources: List[WebConfig]

    @classmethod
    def from_platform(
        cls, payload: config_platform_schemas.PlatformConfigResources
    ) -> "WebConfigResources":
        return cls.model_construct(
            resources=[WebConfig.from_platform(config) for config in payload.resources],
        )


VALID_IP_REGEX = (
    r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4]["
    r"0-9]|25[0-5])$"
)
VALID_HOST_NAME_REGEX = (
    r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9]["
    r"A-Za-z0-9\-]*[A-Za-z0-9])$"
)


def validate_host(host_name):
    if not re.match(VALID_IP_REGEX, host_name) and not re.match(VALID_HOST_NAME_REGEX, host_name):
        raise ValueError(
            "Invalid host format. Must be IPv4 address, IPv6 address, or valid domain name."
        )
    return host_name


class WebUpdateOrCreateConfig(WebBaseSchema):
    MLLP_HOST: Annotated[str, BeforeValidator(validate_host)]
    MLLP_PORT: conint(ge=0, lt=65536)
    MLLP_EXPORT_INTERVAL_MINUTES: conint(gt=0, le=100)

    def to_platform(self) -> config_platform_schemas.PlatformUpdateConfigBatch:
        platform_configs = []

        for field_name, _ in self.__fields__.items():
            value = getattr(self, field_name)
            platform_configs.append(
                config_platform_schemas.PlatformConfig(key=field_name, value=str(value))
            )

        return config_platform_schemas.PlatformUpdateConfigBatch.model_construct(
            configs=platform_configs
        )


class WebUpdateOrCreateConfigPayload(WebBaseSchema):
    password: SecretString
    config: WebUpdateOrCreateConfig


class WebBatchCreateOrUpdateConfigs(WebBaseSchema):
    resources: List[WebUpdateOrCreateConfig]

    @staticmethod
    def to_platform(
        resources: List[WebUpdateOrCreateConfig],
    ):
        configs = [config.to_platform() for config in resources]
        flat_configs = [item for sublist in configs for item in sublist]
        return config_platform_schemas.PlatformUpdateConfigBatch.model_construct(
            configs=flat_configs
        )
