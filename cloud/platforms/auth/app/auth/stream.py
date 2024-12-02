from app.auth.models import User
from app.common.event_sourcing.stream import BaseEventStream


class UserEventStream(BaseEventStream[User]):
    pass
