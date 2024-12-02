from typing import Any, Dict, List, Union

from pydantic import (
    BaseModel,
    ConfigDict,
)


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True,
        populate_by_name=True,
    )


class ErrorSchema(BaseSchema):
    loc: List[str]
    msg: Union[str, List[str]]
    type: str
    ctx: Dict[str, Any] = {}


class ErrorsSchema(BaseSchema):
    detail: List[ErrorSchema]


class WebBaseSchema(BaseSchema):
    pass
