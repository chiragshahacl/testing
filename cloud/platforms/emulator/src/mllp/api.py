from fastapi import APIRouter

from src.mllp.schemas import MLLPMessage
from src.mllp.server import mllp_buffer

api = APIRouter()


@api.get("/mllp")
def get_latest_mllp_messages(limit: int = 10) -> list[MLLPMessage]:
    return [mllp_buffer.pop() for _ in range(limit) if len(mllp_buffer)]
