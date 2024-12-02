import pytest
from features.factories.broker import BrokerMessageFactory, BrokerMessageHeadersFactory

from app.event_processing.subscriber import EventSubscriber, HeaderEventTypes


class TestEventSubscriber:
    def test_register_event_type_handler(self, mocker):
        subscriber = EventSubscriber()
        handler = mocker.AsyncMock()

        subscriber.register_event_type_handler(HeaderEventTypes.ALERT_OBSERVATION_EVENT, handler)

        assert subscriber._key_handlers == {HeaderEventTypes.ALERT_OBSERVATION_EVENT: [handler]}
        subscriber._key_handlers = {}
        EventSubscriber().reset()

    def test_register_topic_handler(self, mocker):
        subscriber = EventSubscriber()
        handler = mocker.AsyncMock()

        subscriber.register_topic_handler("topic", handler)

        assert subscriber._key_handlers == {"topic": [handler]}
        subscriber._key_handlers = {}
        EventSubscriber().reset()

    @pytest.mark.asyncio
    async def test_notify(self, mocker):
        gather_mock = mocker.patch(
            "app.event_processing.subscriber.asyncio.gather", mocker.AsyncMock()
        )
        handler_topic = mocker.AsyncMock()
        handler_event_type = mocker.AsyncMock()
        subscriber = EventSubscriber()
        subscriber.register_topic_handler("topic", handler_topic)
        subscriber.register_event_type_handler("event", handler_event_type)
        headers = BrokerMessageHeadersFactory.build(event_type="event")
        message = BrokerMessageFactory.build(headers=headers, source_topic="topic")

        await subscriber.notify(message)

        gather_mock.assert_awaited()
        EventSubscriber().reset()
