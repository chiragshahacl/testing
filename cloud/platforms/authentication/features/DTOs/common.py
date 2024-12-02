from typing import Any

from pydantic import AnyHttpUrl, BaseModel


class BasePaginationDTO(BaseModel):
    count: int
    next: AnyHttpUrl | None
    previous: AnyHttpUrl | None
    resources: list[Any]
