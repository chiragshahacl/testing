import uuid

from pydantic import BaseModel

from features.DTOs.common import BasePaginationDTO


class UserDTO(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str


class UserPaginationDTO(BasePaginationDTO):
    resources: list[UserDTO]
