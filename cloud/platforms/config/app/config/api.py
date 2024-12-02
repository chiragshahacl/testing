from fastapi import APIRouter, Depends

from app.config.schemas import SystemSettingsSchema
from app.config.services import SystemSettingsService
from app.settings import config

api = APIRouter(prefix=config.BASE_PATH)


@api.get("/system-settings")
async def get_current_system_settings(
    service: SystemSettingsService = Depends(),
) -> SystemSettingsSchema:
    return await service.get_system_settings()
