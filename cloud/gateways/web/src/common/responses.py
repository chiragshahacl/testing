from fastapi.responses import JSONResponse
from pydantic import BaseModel


class FastJSONResponse(JSONResponse):
    """
    Custom FastAPI response to avoid double pydantic validation,
    see `https://github.com/tiangolo/fastapi/discussions/9059`

    Make sure that the model's json encoder is orjson.
    """

    media_type = "application/json"

    def render(self, content: BaseModel) -> bytes:
        return content.model_dump_json(by_alias=True).encode()
