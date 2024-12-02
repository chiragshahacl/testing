from typing import Annotated, Any, Dict, List

from pydantic import BaseModel, ConfigDict, PlainSerializer, SecretStr


class BaseSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class ErrorSchema(BaseSchema):
    loc: List[str]
    msg: str
    type: str
    ctx: Dict[str, Any] = {}


class ErrorsSchema(BaseSchema):
    detail: List[ErrorSchema]


SecretString = Annotated[
    SecretStr,
    PlainSerializer(lambda v: v.get_secret_value() if v else None, when_used="json"),
]
