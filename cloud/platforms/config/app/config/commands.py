from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from app.config.schemas import SystemSettingsPayload
from app.config.services import SystemSettingsService
from app.settings import config

api = APIRouter(prefix=config.BASE_PATH)


@api.post("/UpdateSystemSettings")
async def update_system_settings(
    payload: SystemSettingsPayload, service: SystemSettingsService = Depends()
):
    await service.update_system_settings(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
