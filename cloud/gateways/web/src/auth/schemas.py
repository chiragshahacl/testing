from common_schemas import SecretString
from pydantic import StringConstraints
from typing_extensions import Annotated

from src.common.platform.auth.schemas import (
    PlatformChangePasswordPayload,
    PlatformLogout,
)
from src.common.schemas import WebBaseSchema
from src.settings import settings


class InternalToken(WebBaseSchema):
    access: SecretString
    refresh: SecretString


class RefreshedInternalToken(WebBaseSchema):
    access: SecretString


class RefreshToken(WebBaseSchema):
    refresh: SecretString


class LoginCredential(WebBaseSchema):
    username: str = settings.DEFAULT_ADMIN_USERNAME
    password: Annotated[SecretString, StringConstraints(min_length=1)]


class TechnicalLoginCredential(WebBaseSchema):
    username: str = settings.DEFAULT_TECHNICAL_USER_USERNAME
    password: Annotated[SecretString, StringConstraints(min_length=1)]


class LogoutSchema(WebBaseSchema):
    password: SecretString

    def to_platform(self) -> PlatformLogout:
        return PlatformLogout.model_construct(password=self.password)


class WebChangePasswordPayload(WebBaseSchema):
    current: SecretString
    new: SecretString

    def to_platform(self) -> PlatformChangePasswordPayload:
        return PlatformChangePasswordPayload.model_construct(
            new_password=self.new,
            current_password=self.current,
        )
