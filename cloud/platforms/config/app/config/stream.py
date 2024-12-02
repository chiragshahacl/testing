from app.common.event_sourcing.stream import BaseEventStream
from app.config.schemas import SystemSettingsPayload


class SystemSettingsEventStream(BaseEventStream[SystemSettingsPayload]):
    pass
