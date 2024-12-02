import pytest

from src.realtime.subscriber import (
    BackfillFilter,
    Connection,
    ConnectionManager,
    MetricCodeFilter,
    PatientFilter,
)
from src.streams import BrokerMessage
from tests.factories.broker import BrokerMessageFactory, BrokerMessageHeadersFactory


class TestPatientFilter:
    @pytest.mark.parametrize(
        "key,code,patient_primary_identifier,expected",
        [
            ("wrong-patient-id", "wrong-code-1", "wrong-patient-id", False),
            ("wrong-patient-id", "wrong-code-1", "correct-patient-id", False),
            ("wrong-patient-id", "correct-code", "wrong-patient-id", False),
            ("wrong-patient-id", "correct-code", "correct-patient-id", True),
            ("correct-patient-id", "wrong-code-1", "wrong-patient-id", False),
            ("correct-patient-id", "wrong-code-1", "correct-patient-id", False),
            ("correct-patient-id", "correct-code", "wrong-patient-id", True),
            ("correct-patient-id", "correct-code", "correct-patient-id", True),
        ],
    )
    def test_should_send_message(self, key, code, patient_primary_identifier, expected):
        data_filter = PatientFilter(identifier="correct-patient-id", codes=["correct-code"])
        message = BrokerMessageFactory.build(
            key=key,
            headers=BrokerMessageHeadersFactory.build(
                code=code,
                patient_primary_identifier=patient_primary_identifier,
            ),
        )

        result = data_filter.should_send_message(message)

        assert result is expected


class TestMetricCodeFilter:
    @pytest.mark.parametrize(
        "key,code,expected",
        [
            ("key", "wrong-code-1", False),
            ("key", "correct-code-1", True),
            ("key", "correct-code-2", True),
        ],
    )
    def test_should_send_message(self, key, code, expected):
        data_filter = MetricCodeFilter(codes=["correct-code-1", "correct-code-2"])
        message = BrokerMessageFactory.build(
            key=key,
            headers=BrokerMessageHeadersFactory.build(
                code=code,
            ),
        )

        result = data_filter.should_send_message(message)

        assert result is expected


class TestBackfillFilter:
    @pytest.mark.parametrize(
        "key,isBackfill,expected",
        [
            ("key", "0", True),
            ("key2", "1", False),
        ],
    )
    def test_should_send_message(self, key, isBackfill, expected):
        data_filter = BackfillFilter()
        message = BrokerMessageFactory.build(
            key=key,
            headers=BrokerMessageHeadersFactory.build(
                is_backfill=isBackfill,
            ),
        )

        result = data_filter.should_send_message(message)

        assert result is expected


class FakeConnection(Connection):
    async def refresh(self, message: BrokerMessage) -> None:
        pass


class TestConnection:
    def test_init(self, mocker):
        ws = mocker.Mock()

        topic_subscription = FakeConnection(ws)

        assert topic_subscription._ws == ws

    def test_key(self, mocker):
        ws = mocker.Mock()
        topic_subscription = FakeConnection(ws)

        result = topic_subscription.key()

        assert result == (ws,)

    def test_update_filters(self, mocker):
        ws = mocker.Mock()
        topic_subscription = FakeConnection(ws)
        filters = [mocker.Mock(), mocker.Mock()]

        topic_subscription.update_filters(filters)

        assert topic_subscription._filters == filters

    @pytest.mark.asyncio
    async def test_publish_no_filters(self, mocker):
        ws = mocker.Mock(send_text=mocker.AsyncMock())
        channels = {"topic"}
        topic_subscription = FakeConnection(ws)
        topic_subscription.update_channels(channels)
        topic_subscription.update_filters([])
        data = "message-content"
        message = mocker.Mock(value=data, key="topic")

        await topic_subscription.publish(message, broadcast=False)

        ws.send_text.assert_not_awaited()


class TestSubscriptionManager:
    @pytest.mark.asyncio
    async def test_subscribe_and_notify(self, mocker):
        ws = mocker.Mock(send_text=mocker.AsyncMock())
        manager = ConnectionManager()
        patient_identifier = "PX-001"
        message = BrokerMessageFactory.build(key=patient_identifier)
        connection = FakeConnection(ws)
        connection.update_channels([patient_identifier])

        manager.subscribe(connection)
        await manager.notify(message)

        ws.send_text.assert_awaited_once_with(message.value)

    @pytest.mark.asyncio
    async def test_subscribe_all(self, mocker):
        ws = mocker.Mock(send_text=mocker.AsyncMock())
        manager = ConnectionManager()
        patient_identifier_1 = "PX-001"
        patient_identifier_2 = "PX-002"
        message_1 = BrokerMessageFactory.build(key=patient_identifier_1, value="payload1")
        message_2 = BrokerMessageFactory.build(key=patient_identifier_2, value="payload2")
        connection = FakeConnection(ws)
        connection.update_channels([patient_identifier_1, patient_identifier_2])

        manager.subscribe(connection)
        await manager.notify(message_1)
        await manager.notify(message_2)

        ws.send_text.assert_any_await(message_1.value)
        ws.send_text.assert_any_await(message_2.value)

    @pytest.mark.asyncio
    async def test_unsubscribe(self, mocker):
        ws = mocker.Mock(send_text=mocker.AsyncMock())
        manager = ConnectionManager()
        patient_identifier = "PX-001"
        message = BrokerMessageFactory.build(key=patient_identifier)
        connection = FakeConnection(ws)
        connection.update_channels([patient_identifier])

        manager.subscribe(connection)
        manager.unsubscribe(connection)

        await manager.notify(message)

        ws.send_text.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_broadcast(self, mocker):
        ws = mocker.Mock(send_text=mocker.AsyncMock())
        manager = ConnectionManager()
        patient_identifier = "PX-001"
        message = BrokerMessageFactory.build(key=patient_identifier)
        connection = FakeConnection(ws)
        connection.update_channels([patient_identifier])

        manager.subscribe(connection)

        await manager.broadcast(message)

        ws.send_text.assert_awaited_once_with(message.value)

    @pytest.mark.asyncio
    async def test_notify_error(self, mocker):
        ws = mocker.Mock(send_text=mocker.AsyncMock(side_effect=RuntimeError))
        manager = ConnectionManager()
        patient_identifier = "PX-001"
        message = BrokerMessageFactory.build(key=patient_identifier)
        connection = FakeConnection(ws)
        connection.update_channels([patient_identifier])

        manager.subscribe(connection)
        await manager.notify(message)

        assert connection not in manager._connections

    @pytest.mark.asyncio
    async def test_with_filters(self, mocker):
        manager = ConnectionManager()
        patient_identifier = "PX-001"
        filters = [
            MetricCodeFilter(codes=["code-1", "code-2"]),
            PatientFilter(identifier=patient_identifier, codes=["code-3", "code-4"]),
        ]
        ws = mocker.Mock(send_text=mocker.AsyncMock())
        expected_messages = [
            BrokerMessageFactory.build(
                key="PX-OTHER",
                headers=BrokerMessageHeadersFactory.build(event_type="NEW_METRICS", code="code-1"),
            ),
            BrokerMessageFactory.build(
                key=patient_identifier,
                headers=BrokerMessageHeadersFactory.build(
                    event_type="NEW_WAVEFORM_VITALS", code="code-3"
                ),
            ),
            BrokerMessageFactory.build(
                key=patient_identifier,
                headers=BrokerMessageHeadersFactory.build(
                    event_type="NEW_WAVEFORM_VITALS", code="code-2"
                ),
            ),
            BrokerMessageFactory.build(
                key="PX-OTHER",
                headers=BrokerMessageHeadersFactory.build(
                    event_type="NEW_ALERT_OBSERVATION", code="alert-code"
                ),
            ),
        ]
        messages_to_be_filtered = [
            BrokerMessageFactory.build(
                key="PX-OTHER",
                headers=BrokerMessageHeadersFactory.build(event_type="NEW_METRICS", code="code-4"),
            ),
            BrokerMessageFactory.build(
                key=patient_identifier,
                headers=BrokerMessageHeadersFactory.build(
                    event_type="NEW_WAVEFORM_VITALS", code="code-5"
                ),
            ),
        ]
        connection = FakeConnection(ws)
        connection.update_channels(["PX-OTHER", patient_identifier])

        manager.subscribe(connection)
        connection.update_filters(filters)

        for m in expected_messages + messages_to_be_filtered:
            await manager.notify(m)

        assert ws.send_text.await_count == len(expected_messages)
        ws.send_text.assert_has_awaits([mocker.call(m.value) for m in expected_messages])
