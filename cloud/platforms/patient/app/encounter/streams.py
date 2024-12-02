from app.common.event_sourcing.stream import BaseEventStream
from app.encounter.models import Encounter


class EncounterEventStream(BaseEventStream[Encounter]):
    pass
