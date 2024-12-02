from typing import Any, Dict, List

from pydantic import BaseModel


class ErrorSchema(BaseModel):
    loc: List[str]
    msg: str
    type: str
    ctx: Dict[str, Any] = {}
