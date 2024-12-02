from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class ErrorSchema(BaseSchema):
    loc: List[str]
    msg: str
    type: str
    ctx: Dict[str, Any] = {}


class ErrorsSchema(BaseSchema):
    detail: List[ErrorSchema]
