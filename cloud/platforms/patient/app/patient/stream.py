from app.common.event_sourcing.stream import BaseEventStream
from app.common.models import Bed, BedGroup, Observation, Patient


class PatientEventStream(BaseEventStream[Patient]):
    pass


class BedEventStream(BaseEventStream[Bed]):
    pass


class BedGroupEventStream(BaseEventStream[BedGroup]):
    pass


class ObservationEventStream(BaseEventStream[Observation]):
    pass
