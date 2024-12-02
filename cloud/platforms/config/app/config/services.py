from fastapi import Depends
from starlette.requests import Request

from app.common import kafka_admin
from app.config.events import UpdateSystemSettingsEvent
from app.config.models import SystemSettings
from app.config.repository import ReadSystemSettingsRepository
from app.config.schemas import SystemSettingsPayload, SystemSettingsSchema
from app.config.stream import SystemSettingsEventStream
from app.settings import config


class SystemSettingsService:
    def __init__(
        self,
        request: Request,
        event_stream: SystemSettingsEventStream = Depends(),
        read_system_settings_repository: ReadSystemSettingsRepository = Depends(),
    ):
        self.username = request.state.username
        self.event_stream = event_stream
        self.read_system_settings_repository = read_system_settings_repository

    async def _get_system_settings(self) -> SystemSettings:
        return await self.read_system_settings_repository.get()

    async def get_system_settings(self) -> SystemSettingsSchema:
        current_settings = await self._get_system_settings()
        return SystemSettingsSchema.model_validate(current_settings)

    async def update_system_settings(self, payload: SystemSettingsPayload) -> SystemSettings:
        current_settings = await self._get_system_settings()

        if payload.patient_vitals_retention_time_changed(
            current_settings.patient_vitals_retention_period_ms
        ):
            kafka_admin.change_topic_retention(
                config.PATIENT_VITALS_KAFKA_TOPIC_NAME, payload.patient_vitals_retention_period_ms
            )

        event = UpdateSystemSettingsEvent(self.username, payload)
        await self.event_stream.add(event, current_settings)
