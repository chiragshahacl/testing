from app.common.event_sourcing.stream import BaseEventStream
from app.common.models import AlertLog


class AlertLogEventStream(BaseEventStream[AlertLog]):
    pass
