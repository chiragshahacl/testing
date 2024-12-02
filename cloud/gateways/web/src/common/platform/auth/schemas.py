from common_schemas import SecretString

from src.common.schemas import BaseSchema


class PlatformLogout(BaseSchema):
    password: SecretString


class PlatformChangePasswordPayload(BaseSchema):
    current_password: SecretString
    new_password: SecretString
