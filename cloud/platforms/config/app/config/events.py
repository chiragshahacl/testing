from app.common.event_sourcing.events import Event
from app.config.models import SystemSettings
from app.config.schemas import SystemSettingsPayload


class UpdateSystemSettingsEvent(Event):
    display_name: str = "System settings updated"
    event_type: str = "SYSTEM_SETTINGS_UPDATED_EVENT"

    def __init__(self, username: str, settings: SystemSettingsPayload):
        super().__init__(username)
        self.settings = settings

    def process(self, entity: SystemSettings) -> SystemSettings:
        if self.settings.patient_vitals_retention_period_ms:
            entity.patient_vitals_retention_period_ms = (
                self.settings.patient_vitals_retention_period_ms
            )
        return entity
