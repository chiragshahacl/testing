import pytest

from src.common.enums import HeaderEventTypes
from src.streams import (
    BrokerMessage,
    BrokerMessageHeaders,
    EventSubscriber,
)
from tests.factories.broker import (
    BrokerMessageFactory,
    BrokerMessageHeadersFactory,
    KafkaMessageFactory,
)


class TestBrokerMessageHeaders:
    def test_init(self):
        data = {
            "event_type": "type",
            "code": "1234",
            "device_primary_identifier": "SENSOR-01",
        }

        result = BrokerMessageHeaders(**data)

        assert result.event_type == "type"
        assert result.code == "1234"
        assert result.device_primary_identifier == "SENSOR-01"

    def test_init_with_minimal_data(self):
        data = {"event_type": "type"}

        result = BrokerMessageHeaders(**data)

        assert result.event_type == "type"
        assert result.code is None
        assert result.device_primary_identifier is None


class TestBrokerMessage:
    def test_init(self):
        headers = BrokerMessageHeadersFactory.build()
        message = BrokerMessage(key="key", value="value", source_topic="source", headers=headers)

        assert message.key == "key"
        assert message.value == "value"
        assert message.source_topic == "source"
        assert message.headers == headers

    def test_from_kafka_message_minimal_headers(self):
        kafka_message = KafkaMessageFactory.build(headers=(("event_type", b"NEW_METRIC"),))

        result = BrokerMessage.from_kafka_message(kafka_message)

        assert result.key == kafka_message.key
        assert result.value == kafka_message.value
        assert result.source_topic == kafka_message.topic
        assert result.headers.event_type == "NEW_METRIC"
        assert result.headers.code is None
        assert result.headers.device_primary_identifier is None

    def test_from_kafka_message(self):
        kafka_message = KafkaMessageFactory.build(
            headers=(
                ("event_type", b"NEW_METRIC"),
                ("code", b"1234"),
                ("device_primary_identifier", b"DEV-ID"),
            )
        )

        result = BrokerMessage.from_kafka_message(kafka_message)

        assert result.key == kafka_message.key
        assert result.value == kafka_message.value
        assert result.source_topic == kafka_message.topic
        assert result.headers.event_type == "NEW_METRIC"
        assert result.headers.code == "1234"
        assert result.headers.device_primary_identifier == "DEV-ID"


class TestEventSubscriber:
    def test_register_event_type_handler(self, mocker):
        subscriber = EventSubscriber()
        handler = mocker.Mock()

        subscriber.register_event_type_handler(HeaderEventTypes.NEW_METRICS, handler)

        assert subscriber._key_handlers == {HeaderEventTypes.NEW_METRICS: [handler]}
        subscriber._key_handlers = {}

    def test_register_topic_handler(self, mocker):
        subscriber = EventSubscriber()
        handler = mocker.Mock()

        subscriber.register_topic_handler("topic", handler)

        assert subscriber._key_handlers == {"topic": [handler]}
        subscriber._key_handlers = {}

    @pytest.mark.asyncio
    async def test_notify(self, mocker):
        gather_mock = mocker.patch("src.streams.asyncio.gather", mocker.AsyncMock())
        handler_topic = mocker.Mock()
        handler_event_type = mocker.Mock()
        subscriber = EventSubscriber()
        subscriber.register_topic_handler("topic", handler_topic)
        subscriber.register_event_type_handler("event", handler_event_type)
        headers = BrokerMessageHeadersFactory.build(event_type="event")
        message = BrokerMessageFactory.build(headers=headers, source_topic="topic")

        await subscriber.notify(message)

        gather_mock.assert_awaited()
