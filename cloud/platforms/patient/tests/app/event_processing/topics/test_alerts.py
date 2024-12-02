import json
import uuid

import pytest
from features.environment import AnyDateTime, AnyUUID
from features.factories.broker import BrokerMessageFactory
from features.factories.device_factories import DeviceFactory
from features.factories.encounter import EncounterFactory
from features.factories.observation_factories import (
    ObservationFactory,
)
from features.factories.patient_factories import PatientFactory
from features.factories.physiological_alert_factory import PhysiologicalAlertFactory
from features.factories.sdc import (
    SDCAlertPayloadFactory,
    SDCNewAlertEventFactory,
    SDCPatientSessionClosedEventFactory,
    SDCPatientSessionClosedPayloadFactory,
)
from sqlalchemy import select

from app.common.models import AlertLog, Observation
from app.event_processing.topics.alerts.processors import (
    insert_alert_state_in_audit_log,
    process_physiological_incoming_alert_event,
)
from app.event_processing.topics.events_sdc.processors import (
    clean_alert_state_audit_log_when_subject_is_removed,
)
from app.patient.events import (
    ActivateAlertEvent,
    DeactivateAlertEvent,
)
from app.settings import config


@pytest.mark.asyncio
async def test_new_alert_event(async_db_session, producer_mock):
    message = SDCNewAlertEventFactory.build()
    patient = PatientFactory.build(
        primary_identifier=message.payload.patient_primary_identifier,
    )
    async_db_session.add(patient)
    await async_db_session.flush()
    broker_message = BrokerMessageFactory.build(
        value=message.model_dump_json(), source_topic=config.EVENTS_ALERT_TOPIC
    )

    await process_physiological_incoming_alert_event(async_db_session, broker_message)

    stmt = select(Observation).where(
        Observation.code == message.payload.code,
        Observation.subject_id == patient.id,
    )
    result = await async_db_session.execute(stmt)
    observation = result.scalars().one_or_none()

    assert observation
    assert str(observation.subject_id) == patient.id
    assert observation.code == message.payload.code
    assert observation.value_text == message.payload.priority
    assert observation.is_alert is True
    assert observation.effective_dt == message.payload.determination_time


@pytest.mark.asyncio
async def test_inactive_alert_event(async_db_session, producer_mock):
    payload = SDCAlertPayloadFactory.build(active=False)
    message = SDCNewAlertEventFactory.build(payload=payload)
    patient = PatientFactory.build(
        primary_identifier=message.payload.patient_primary_identifier,
    )
    observation = ObservationFactory.build(subject_id=patient.id)
    async_db_session.add(patient)
    await async_db_session.flush()
    async_db_session.add(observation)
    await async_db_session.flush()
    broker_message = BrokerMessageFactory.build(
        value=message.model_dump_json(), source_topic=config.EVENTS_ALERT_TOPIC
    )

    await process_physiological_incoming_alert_event(async_db_session, broker_message)

    stmt = select(Observation).where(
        Observation.code == message.payload.code,
        Observation.subject_id == patient.id,
    )
    result = await async_db_session.execute(stmt)
    found_observations = result.scalars().all()
    assert not found_observations


@pytest.mark.asyncio
async def test_new_alert_patient_is_none(async_db_session, producer_mock):
    payload = SDCAlertPayloadFactory.build(active=False)
    message = SDCNewAlertEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=message.model_dump_json())

    await process_physiological_incoming_alert_event(async_db_session, broker_message)

    stmt = select(Observation)
    result = await async_db_session.execute(stmt)
    found_observations = result.scalars().all()

    assert not found_observations


@pytest.mark.asyncio
async def test_backfill_alert_event(async_db_session, producer_mock):
    payload = SDCAlertPayloadFactory.build(is_backfill=True)
    message = SDCNewAlertEventFactory.build(payload=payload)
    patient = PatientFactory.build(
        primary_identifier=message.payload.patient_primary_identifier,
    )
    async_db_session.add(patient)
    await async_db_session.flush()
    broker_message = BrokerMessageFactory.build(value=message.model_dump_json())

    await process_physiological_incoming_alert_event(async_db_session, broker_message)

    stmt = select(Observation).where(
        Observation.code == message.payload.code,
        Observation.subject_id == patient.id,
    )
    result = await async_db_session.execute(stmt)
    found_observations = result.scalars().all()

    assert not found_observations


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "active,latching,event_class",
    [
        (True, False, ActivateAlertEvent),
        (False, False, DeactivateAlertEvent),
        (True, True, DeactivateAlertEvent),
    ],
)
async def test_insert_alert_state_in_audit_log_alert_activated(
    async_db_session, producer_mock, active, latching, event_class
):
    payload = SDCAlertPayloadFactory.build(active=active, latching=latching)
    incoming_alert = SDCNewAlertEventFactory.build(payload=payload)
    patient = PatientFactory.build(
        primary_identifier=incoming_alert.payload.patient_primary_identifier,
    )
    async_db_session.add(patient)
    await async_db_session.flush()
    broker_message = BrokerMessageFactory.build(
        value=incoming_alert.model_dump_json(), source_topic=config.EVENTS_ALERT_TOPIC
    )

    await insert_alert_state_in_audit_log(async_db_session, broker_message)

    stmt = select(AlertLog).where(AlertLog.patient_id == patient.id)
    result = await async_db_session.execute(stmt)
    alerts = result.scalars().all()

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.code == incoming_alert.payload.code
    assert str(alert.patient_id) == patient.id
    assert alert.active == (incoming_alert.payload.active and not incoming_alert.payload.latching)
    assert alert.device_primary_identifier == incoming_alert.payload.device_primary_identifier
    assert alert.determination_time == incoming_alert.payload.determination_time
    assert alert.value_text == incoming_alert.payload.priority
    assert producer_mock.send_and_wait.call_count == 1

    actual_topic = producer_mock.send_and_wait.call_args[1]["topic"]
    actual_headers = producer_mock.send_and_wait.call_args[1]["headers"]
    actual_value = json.loads(producer_mock.send_and_wait.call_args[1]["value"])
    assert actual_topic == config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    assert actual_headers == [("event_type", event_class.event_type.encode())]
    assert actual_value == {
        "entity_id": str(patient.id),
        "event_name": event_class.display_name,
        "performed_on": AnyDateTime(),
        "performed_by": "system",
        "event_state": {
            "active": incoming_alert.payload.active and not incoming_alert.payload.latching,
            "code": incoming_alert.payload.code,
            "determination_time": incoming_alert.payload.determination_time.isoformat(),
            "device_code": incoming_alert.payload.device_code,
            "device_primary_identifier": incoming_alert.payload.device_primary_identifier,
            "trigger_upper_limit": incoming_alert.payload.vital_range.upper_limit,
            "trigger_lower_limit": incoming_alert.payload.vital_range.lower_limit,
            "patient_id": str(patient.id),
            "patient_primary_identifier": str(patient.primary_identifier),
            "value_text": incoming_alert.payload.priority,
        },
        "previous_state": {},
        "event_type": event_class.event_type,
        "message_id": AnyUUID(),
        "event_data": {
            "code": incoming_alert.payload.code,
            "patient_id": str(patient.id),
            "patient_primary_identifier": str(patient.primary_identifier),
            "determination_time": incoming_alert.payload.determination_time.isoformat(),
            "value_text": incoming_alert.payload.priority,
            "device_primary_identifier": incoming_alert.payload.device_primary_identifier,
            "trigger_upper_limit": incoming_alert.payload.vital_range.upper_limit,
            "trigger_lower_limit": incoming_alert.payload.vital_range.lower_limit,
            "device_code": incoming_alert.payload.device_code,
            "active": incoming_alert.payload.active and not incoming_alert.payload.latching,
        },
        "entity_name": "patient",
        "emitted_by": "patient",
    }


@pytest.mark.asyncio
async def test_alert_log_cleaned_when_patient_session_is_closed(async_db_session):
    patient = PatientFactory.build(id=uuid.uuid4())
    async_db_session.add(patient)
    device = DeviceFactory.build(id=uuid.uuid4())
    async_db_session.add(device)
    await async_db_session.flush()
    encounter = EncounterFactory.build(
        subject=patient,
        device=device,
    )
    async_db_session.add(encounter)
    await async_db_session.flush()

    inactive_alert = PhysiologicalAlertFactory.build(patient_id=patient.id, active=False)
    active_alert = PhysiologicalAlertFactory.build(patient_id=patient.id, active=True)
    async_db_session.add(inactive_alert)
    async_db_session.add(active_alert)
    await async_db_session.flush()

    message = SDCPatientSessionClosedEventFactory.build(
        payload=SDCPatientSessionClosedPayloadFactory.build(
            device_primary_identifier=device.primary_identifier
        )
    )
    broker_message = BrokerMessageFactory.build(value=message.model_dump_json())

    await clean_alert_state_audit_log_when_subject_is_removed(async_db_session, broker_message)

    stmt = select(AlertLog).where(AlertLog.patient_id == patient.id)
    result = await async_db_session.execute(stmt)
    alerts = result.scalars().all()
    assert not alerts
