import datetime
import json

import pytest
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from src.audit.consumer import (
    KafkaClient,
    KafkaClientFactory,
    insert_audit_trail_event,
    internal_audit_trail_consumer,
)
from src.audit.schemas import IncomingMessageSchema
from src.settings import settings


class TestKafkaClientFactory:
    def test_init(self):
        factory = KafkaClientFactory()

        assert factory.client is None

    @pytest.mark.asyncio
    async def test_call_local_env(self, mocker):
        factory = KafkaClientFactory()
        mocker.patch.object(settings, "ENVIRONMENT", "local")
        consumer_mock = mocker.AsyncMock(spec=AIOKafkaConsumer)
        aio_consumer_mock = mocker.patch(
            "src.audit.consumer.AIOKafkaConsumer", return_value=consumer_mock
        )

        client = await factory()

        aio_consumer_mock.assert_called_once_with(
            settings.PATIENT_EVENTS_TOPIC,
            settings.AUTH_EVENTS_TOPIC,
            settings.DEVICE_EVENTS_TOPIC,
            group_id=settings.CONSUMER_AUDIT_TRAIL_GROUP_ID,
            bootstrap_servers=f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
            retry_backoff_ms=settings.KAFKA_RETRY_BACKOFF,
            metadata_max_age_ms=settings.KAFKA_METADATA_MAX_AGE,
        )
        assert client is aio_consumer_mock.return_value

    @pytest.mark.asyncio
    async def test_call_non_local_env(self, mocker):
        factory = KafkaClientFactory()
        mocker.patch.object(settings, "ENVIRONMENT", "other")
        consumer_mock = mocker.AsyncMock(spec=AIOKafkaConsumer)
        consumer_mock.start = mocker.AsyncMock()
        aio_consumer_mock = mocker.patch(
            "src.audit.consumer.AIOKafkaConsumer", return_value=consumer_mock
        )
        create_ssl_context_mock = mocker.patch("src.audit.consumer.create_ssl_context")

        client = await factory()

        create_ssl_context_mock.assert_called_once_with(
            cafile=settings.KAFKA_CA_FILE_PATH,
            certfile=settings.KAFKA_CERT_FILE_PATH,
            keyfile=settings.KAFKA_KEY_FILE_PATH,
            password=settings.KAFKA_PASSWORD,
        )
        aio_consumer_mock.assert_called_once_with(
            settings.PATIENT_EVENTS_TOPIC,
            settings.AUTH_EVENTS_TOPIC,
            settings.DEVICE_EVENTS_TOPIC,
            group_id=settings.CONSUMER_AUDIT_TRAIL_GROUP_ID,
            bootstrap_servers=f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
            security_protocol="SSL",
            ssl_context=create_ssl_context_mock.return_value,
            retry_backoff_ms=settings.KAFKA_RETRY_BACKOFF,
            metadata_max_age_ms=settings.KAFKA_METADATA_MAX_AGE,
        )
        assert client is aio_consumer_mock.return_value


@pytest.mark.asyncio
async def test_insert_audit_trail_event(mocker):
    db_session_mock = mocker.MagicMock()
    db_session_mock.commit = mocker.AsyncMock()
    session_maker_mock = mocker.patch("src.audit.consumer.session_maker")
    session_maker_mock.return_value.__aenter__.return_value = db_session_mock
    audit_mock = mocker.patch("src.audit.consumer.InternalAudit")
    db_session_mock.add = mocker.MagicMock()
    message = IncomingMessageSchema(
        entity_id="test1",
        event_name="test1",
        performed_on=datetime.datetime.now(),
        performed_by="test1",
        event_state={},
        previous_state={},
        entity_name="test1",
        emitted_by="test1",
        event_type="test1",
        message_id="test1",
    )
    audit_model = audit_mock(
        message_id=message.message_id,
        entity_id=message.entity_id,
        timestamp=message.performed_on,
        event_name=message.event_name,
        data={
            "current_state": message.event_state,
            "previous_state": message.previous_state,
        },
        emitted_by=message.emitted_by,
        performed_by=message.performed_by,
    )

    await insert_audit_trail_event(message)

    db_session_mock.add.assert_called_once_with(audit_model)


@pytest.mark.asyncio
async def test_internal_audit_trail_consumer(mocker):
    message_value = {
        "entity_id": "123e4567-e89b-12d3-a456-426655440000",
        "event_name": "987e6543-21d9-48c6-a987-654321098765",
        "performed_on": "2023-06-22T12:34:56",
        "performed_by": "system",
        "event_state": {},
        "previous_state": {},
        "entity_name": "ABC123",
        "emitted_by": "DEVICE001",
        "event_type": "HI",
        "message_id": "ALERT",
    }
    msg_schema = IncomingMessageSchema(**message_value)
    mock_messages = [mocker.MagicMock(value=json.dumps(message_value))]
    consumer_mock = mocker.AsyncMock(spec=KafkaClient)
    consumer_mock.return_value = mocker.AsyncMock()
    mocker.patch("src.audit.consumer.KafkaClient", consumer_mock)
    consumer_mock.return_value.__aiter__.return_value = mock_messages
    insert_audit_trail_event_mock = mocker.patch("src.audit.consumer.insert_audit_trail_event")
    insert_audit_trail_event_mock.side_effect = KafkaError
    await internal_audit_trail_consumer()
    insert_audit_trail_event_mock.assert_called_once_with(msg_schema)


@pytest.mark.asyncio
async def test_internal_audit_trail_consumer_exception(mocker):
    message_value = {
        "entity_id": "123e4567-e89b-12d3-a456-426655440000",
        "event_name": "987e6543-21d9-48c6-a987-654321098765",
        "performed_on": "2023-06-22T12:34:56",
        "performed_by": "system",
        "event_state": {},
        "previous_state": {},
        "entity_name": "ABC123",
        "emitted_by": "DEVICE001",
        "event_type": "HI",
        "message_id": "ALERT",
    }
    msg_schema = IncomingMessageSchema(**message_value)
    mock_messages = [mocker.MagicMock(value=json.dumps(message_value))]
    consumer_mock = mocker.AsyncMock(spec=KafkaClient)
    consumer_mock.return_value = mocker.AsyncMock()
    mocker.patch("src.audit.consumer.KafkaClient", consumer_mock)
    consumer_mock.return_value.__aiter__.return_value = mock_messages
    insert_audit_trail_event_mock = mocker.patch("src.audit.consumer.insert_audit_trail_event")
    insert_audit_trail_event_mock.side_effect = [Exception("TEST"), KafkaError]
    await internal_audit_trail_consumer()
    insert_audit_trail_event_mock.assert_called_with(msg_schema)
