import abc
import typing
from contextlib import suppress

from loguru import logger
from starlette.exceptions import WebSocketException as StarletteWebSocketException
from starlette.websockets import WebSocket
from websockets.exceptions import WebSocketException

from src.streams import BrokerMessage


class SubscriptionFilter(abc.ABC):
    @abc.abstractmethod
    def should_send_message(self, message: BrokerMessage) -> bool:
        """Returns True if the message should be sent"""


class PatientFilter(SubscriptionFilter):
    def __init__(self, identifier: str, codes: list[str]):
        self.identifier = identifier
        self.codes = set(codes)

    def should_send_message(self, message: BrokerMessage) -> bool:
        return (
            self._is_identifier_on_key(message) or self._is_identifier_on_headers(message)
        ) and self._is_headers_code_allowed(message)

    def _is_headers_code_allowed(self, message):
        return message.headers.code and message.headers.code in self.codes

    def _is_identifier_on_key(self, message):
        return message.key == self.identifier

    def _is_identifier_on_headers(self, message):
        patient_header = message.headers.patient_primary_identifier
        return patient_header and patient_header == self.identifier


class MetricCodeFilter(SubscriptionFilter):
    def __init__(self, codes: list[str]) -> None:
        self.codes = codes

    def should_send_message(self, message: BrokerMessage) -> bool:
        return message.headers.code and message.headers.code in self.codes


class BackfillFilter(SubscriptionFilter):
    def should_send_message(self, message: BrokerMessage) -> bool:
        return message.headers.is_backfill != "1"


class Connection(abc.ABC):
    _ws: WebSocket
    _filters: list[SubscriptionFilter]

    def __init__(self, ws: WebSocket) -> None:
        self._ws = ws
        self._filters = []
        self._channels = []

    def __hash__(self) -> int:
        return hash(self.key())

    def __repr__(self) -> str:
        return f"<Connection ws={self._ws}, channels={self._channels}>"

    def key(self) -> tuple[typing.Any, ...]:
        return (self._ws,)

    def _should_send_message(self, message: BrokerMessage) -> bool:
        if not message.is_vitals_message:
            return True

        if not self._filters:
            return False

        if message.key not in self._channels:
            return False

        return any(f.should_send_message(message) for f in self._filters)

    def update_filters(self, filters: list[SubscriptionFilter]) -> None:
        self._filters = filters

    def update_channels(self, channels: set[str]) -> None:
        self._channels = channels

    async def publish(self, message: BrokerMessage, broadcast: bool = False) -> None:
        if broadcast or self._should_send_message(message):
            await self._ws.send_text(message.value)

    @abc.abstractmethod
    async def refresh(self, message: BrokerMessage) -> None:
        """Apply changes to connection based on message"""


class PatientsSubscription:
    patient_identifiers: set[str]

    def __init__(self, patient_identifiers: list[str]) -> None:
        self.patient_identifiers = set(patient_identifiers)

    def __repr__(self) -> str:
        return f"<PatientsSubscription patients={self.patient_identifiers}>"


class PatientsConnection(Connection):
    _subscription: PatientsSubscription

    def __init__(self, ws: WebSocket, patient_subscription: PatientsSubscription) -> None:
        self._subscription = patient_subscription
        super().__init__(ws)

    async def refresh(self, message: BrokerMessage) -> None:
        pass


class ConnectionManager:
    _instance = None
    _connections: set[Connection] = set()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
        return cls._instance

    def subscribe(self, connection: Connection) -> None:
        self._connections.add(connection)
        logger.debug(f"Subscribed: {connection}")

    def unsubscribe(self, connection: Connection) -> None:
        with suppress(KeyError):
            self._connections.remove(connection)
        logger.debug(f"Unsubscribed: {connection}")

    async def _notify_connections(self, message: BrokerMessage, broadcast: bool = False) -> None:
        for conn in list(self._connections):
            try:
                await conn.publish(message, broadcast=broadcast)
            except (RuntimeError, WebSocketException, StarletteWebSocketException):
                self.unsubscribe(conn)
                logger.debug(f"Removed zombie ws: {conn}")

    async def broadcast(self, message: BrokerMessage) -> None:
        await self._notify_connections(message, broadcast=True)
        logger.debug(f"Broadcasting message: {message}")

    async def notify(self, message: BrokerMessage) -> None:
        await self._notify_connections(message)

    def reset(self):
        self._connections = set()
