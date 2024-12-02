import uuid
from typing import Literal

from django.conf import settings
from pydantic import BaseModel


class SessionDTO(BaseModel):
    access: str
    refresh: str


class RefreshedSessionDTO(BaseModel):
    access: str


class DecodedTokenDTO(BaseModel):
    token_type: Literal["access", "refresh"]
    exp: int
    iat: int
    jti: str
    user_id: uuid.UUID
    username: str
    groups: list[str]
    aud: Literal[settings.SIMPLE_JWT.get("AUDIENCE")]
