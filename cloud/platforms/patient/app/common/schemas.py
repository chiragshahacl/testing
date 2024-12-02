from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import AvailablePageSizes


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True, populate_by_name=True, from_attributes=True
    )


def json_encode(schema: BaseModel, by_alias: bool = False) -> str:
    """
    Encodes a BaseSchema object into JSON using
    FastAPI's encoder function and exposing all secret fields
    """
    return schema.model_dump_json(by_alias=by_alias)


class ErrorSchema(BaseSchema):
    loc: List[str]
    msg: str
    type: str
    ctx: Dict[str, Any] = {}


class ErrorsSchema(BaseSchema):
    detail: List[ErrorSchema]


class PaginationParams(BaseSchema):
    page_number: int = Field(ge=1, default=1)
    page_size: AvailablePageSizes = AvailablePageSizes.TWO_HUNDRED
