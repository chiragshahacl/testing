import json
import uuid
from datetime import datetime

import pytest
from aiokafka import AIOKafkaProducer
from faker import Faker
from features.environment import AnyDateTime, AnyUUID
from features.factories.broker import BrokerMessageFactory
from features.factories.device_factories import DeviceFactory
from features.factories.encounter import EncounterFactory
from features.factories.observation_factories import ObservationFactory
from features.factories.patient_factories import PatientFactory
from features.factories.sdc import (
    SDCAlertPayloadFactory,
    SDCDeviceDiscoveredEventFactory,
    SDCDeviceDiscoveredPayloadFactory,
    SDCDevicePayloadFactory,
    SDCPatientAdmissionRejectedEventFactory,
    SDCPatientAdmissionRejectedPayloadFactory,
    SDCPatientPayloadFactory,
    SDCPatientSessionClosedEventFactory,
    SDCPatientSessionClosedPayloadFactory,
    SDCPatientSessionStartedEventFactory,
    SDCPatientSessionStartedPayloadFactory,
    SDCSensorRemovedEventFactory,
    SDCSensorRemovedPayloadFactory,
)
from sqlalchemy import select

from app.common.models import AlertLog, Observation, Patient
from app.encounter.enums import EncounterStatus
from app.encounter.events import CompletePatientEncounter, StartPatientEncounter
from app.encounter.models import Encounter
from app.event_processing.topics.events_sdc.processors import (
    process_device_discovered_event_for_patient,
    process_patient_admission_rejected,
    process_patient_session_ended_event_for_patient,
    process_patient_session_started_event,
    process_sensor_removed_event_for_patient,
    start_patient_encounter,
)
from app.event_processing.topics.events_sdc.schemas import SDCDeviceDiscoveredEvent
from app.patient.events import (
    ActivateAlertEvent,
    DeactivateAlertEvent,
)
from app.settings import config


@pytest.mark.asyncio
async def test_new_device_discovered(async_db_session, mocker):
    producer_mock = mocker.AsyncMock(spec=AIOKafkaProducer)
    mocker.patch(
        "app.common.event_sourcing.publisher.AIOKafkaProducer",
        return_value=producer_mock,
    )

    patient_payload = SDCPatientPayloadFactory.build()
    device_payload = SDCDevicePayloadFactory.build(connected_sensors=[], alerts=[])
    device_discovered_payload = SDCDeviceDiscoveredPayloadFactory.build(
        patient=patient_payload, device=device_payload
    )
    sdc_message: SDCDeviceDiscoveredEvent = SDCDeviceDiscoveredEventFactory.build(
        payload=device_discovered_payload
    )

    device = DeviceFactory.build(
        id=uuid.uuid4(), primary_identifier=device_payload.primary_identifier
    )
    async_db_session.add(device)
    await async_db_session.flush()

    broker_message = BrokerMessageFactory.build(value=sdc_message.model_dump_json())
    await process_device_discovered_event_for_patient(async_db_session, broker_message)

    stmt = select(Patient).where(
        Patient.primary_identifier == sdc_message.payload.patient.primary_identifier
    )
    result = await async_db_session.execute(stmt)
    patient = result.scalars().one()

    assert patient
    assert patient.primary_identifier == patient_payload.primary_identifier
    assert patient.given_name == patient_payload.given_name_decrypted
    assert patient.family_name == patient_payload.family_name_decrypted
    assert patient.birth_date == patient_payload.birth_date_decrypted
    assert patient.gender == patient_payload.gender


@pytest.mark.asyncio
async def test_new_device_discovered_no_patient(async_db_session, mocker):
    producer_mock = mocker.AsyncMock(spec=AIOKafkaProducer)
    mocker.patch(
        "app.common.event_sourcing.publisher.AIOKafkaProducer",
        return_value=producer_mock,
    )

    device_discovered_payload = SDCDeviceDiscoveredPayloadFactory.build(patient=None)
    sdc_message: SDCDeviceDiscoveredEvent = SDCDeviceDiscoveredEventFactory.build(
        payload=device_discovered_payload
    )
    broker_message = BrokerMessageFactory.build(value=sdc_message.model_dump_json())

    await process_device_discovered_event_for_patient(async_db_session, broker_message)

    result = await async_db_session.execute(select(Patient))
    assert not result.scalars().all()


@pytest.mark.asyncio
async def test_already_discovered_device_discovered_again(async_db_session, mocker):
    producer_mock = mocker.AsyncMock(spec=AIOKafkaProducer)
    mocker.patch(
        "app.common.event_sourcing.publisher.AIOKafkaProducer",
        return_value=producer_mock,
    )

    initial_patient = PatientFactory.build()
    patient_payload = SDCPatientPayloadFactory.build(
        primary_identifier=str(initial_patient.primary_identifier),
        given_name=initial_patient.given_name,
        family_name=initial_patient.family_name,
        gender=initial_patient.gender.value,
        birth_date=initial_patient.birth_date.isoformat(),
    )
    device_payload = SDCDevicePayloadFactory.build(connected_sensors=[], alerts=[])
    device_discovered_payload = SDCDeviceDiscoveredPayloadFactory.build(
        patient=patient_payload, device=device_payload
    )
    sdc_message: SDCDeviceDiscoveredEvent = SDCDeviceDiscoveredEventFactory.build(
        payload=device_discovered_payload
    )
    broker_message = BrokerMessageFactory.build(value=sdc_message.model_dump_json())

    device = DeviceFactory.build(
        id=uuid.uuid4(), primary_identifier=device_payload.primary_identifier
    )
    async_db_session.add(device)
    async_db_session.add(initial_patient)
    await async_db_session.flush()

    await process_device_discovered_event_for_patient(async_db_session, broker_message)

    stmt = select(Patient).where(
        Patient.primary_identifier == patient_payload.primary_identifier,
    )
    result = await async_db_session.execute(stmt)
    patient = result.scalars().one()

    assert patient
    assert patient.primary_identifier == patient_payload.primary_identifier
    assert patient.given_name == patient_payload.given_name_decrypted
    assert patient.family_name == patient_payload.family_name_decrypted
    assert patient.birth_date == patient_payload.birth_date_decrypted
    assert patient.gender == patient_payload.gender


@pytest.mark.asyncio
async def test_process_sensor_removed_event(async_db_session, mocker):
    producer_mock = mocker.AsyncMock(spec=AIOKafkaProducer)
    mocker.patch(
        "app.common.event_sourcing.publisher.AIOKafkaProducer",
        return_value=producer_mock,
    )

    fake_sensor_primary_identifier = Faker().uuid4()

    patient = PatientFactory.build()
    async_db_session.add(patient)
    await async_db_session.flush()

    observation = ObservationFactory.build()
    observation.subject_id = patient.id
    observation.device_primary_identifier = fake_sensor_primary_identifier
    async_db_session.add(observation)
    await async_db_session.flush()

    message = SDCSensorRemovedEventFactory.build(
        payload=SDCSensorRemovedPayloadFactory.build(
            device_primary_identifier=fake_sensor_primary_identifier
        ),
    )
    broker_message = BrokerMessageFactory.build(value=message.model_dump_json())

    await process_sensor_removed_event_for_patient(async_db_session, broker_message)

    result = await async_db_session.execute(
        select(Observation).where(
            Observation.device_primary_identifier == fake_sensor_primary_identifier
        )
    )
    observations_found = result.scalars().all()
    assert not observations_found


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "active,event_class",
    [
        (True, ActivateAlertEvent),
        (False, DeactivateAlertEvent),
    ],
)
async def test_new_device_discovered_with_alerts(
    async_db_session, producer_mock, active, event_class
):
    patient_primary_identifier = Faker().pystr()
    alert_payload = SDCAlertPayloadFactory.build(
        active=active, patient_primary_identifier=patient_primary_identifier
    )
    patient_payload = SDCPatientPayloadFactory.build(
        primary_identifier=patient_primary_identifier, alerts=[alert_payload]
    )
    device_payload = SDCDevicePayloadFactory.build(connected_sensors=[], alerts=[])
    device_discovered_payload = SDCDeviceDiscoveredPayloadFactory.build(
        patient=patient_payload, device=device_payload
    )
    sdc_message: SDCDeviceDiscoveredEvent = SDCDeviceDiscoveredEventFactory.build(
        payload=device_discovered_payload
    )

    device = DeviceFactory.build(
        id=uuid.uuid4(), primary_identifier=device_payload.primary_identifier
    )
    async_db_session.add(device)
    await async_db_session.flush()

    broker_message = BrokerMessageFactory.build(value=sdc_message.model_dump_json())
    await process_device_discovered_event_for_patient(async_db_session, broker_message)

    stmt = select(Patient).where(
        Patient.primary_identifier == sdc_message.payload.patient.primary_identifier
    )
    result = await async_db_session.execute(stmt)
    patient = result.scalars().one()

    assert patient
    assert patient.primary_identifier == patient_payload.primary_identifier
    assert patient.given_name == patient_payload.given_name_decrypted
    assert patient.family_name == patient_payload.family_name_decrypted
    assert patient.birth_date == patient_payload.birth_date_decrypted
    assert patient.gender == patient_payload.gender

    # Assert the alert observation was created
    if active:
        stmt = select(Observation).where(
            Observation.code == alert_payload.code,
            Observation.subject_id == patient.id,
        )
        result = await async_db_session.execute(stmt)
        observation = result.scalars().one_or_none()

        assert observation
        assert observation.subject_id == patient.id
        assert observation.code == alert_payload.code
        assert observation.value_text == alert_payload.priority
        assert observation.is_alert is True
        assert observation.effective_dt == alert_payload.determination_time

    # Assert the alarm audit log was created
    stmt = select(AlertLog).where(AlertLog.patient_id == patient.id)
    result = await async_db_session.execute(stmt)
    alerts = result.scalars().all()

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.code == alert_payload.code
    assert alert.patient_id == patient.id
    assert alert.active == alert_payload.active
    assert alert.device_primary_identifier == alert_payload.device_primary_identifier
    assert alert.determination_time == alert_payload.determination_time
    assert alert.value_text == alert_payload.priority
    # Patient created, multiple alert observation event, alert audit log created
    assert producer_mock.send_and_wait.call_count == 3

    audit_log_message_sent = producer_mock.send_and_wait.call_args_list[-1][1]
    actual_topic = audit_log_message_sent["topic"]
    actual_headers = audit_log_message_sent["headers"]
    actual_value = json.loads(audit_log_message_sent["value"])
    assert actual_topic == config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    assert actual_headers == [("event_type", event_class.event_type.encode())]
    assert actual_value == {
        "entity_id": str(patient.id),
        "event_name": event_class.display_name,
        "performed_on": AnyDateTime(),
        "performed_by": "system",
        "event_state": {
            "active": alert_payload.active,
            "code": alert_payload.code,
            "determination_time": alert_payload.determination_time.isoformat(),
            "device_code": alert_payload.device_code,
            "device_primary_identifier": alert_payload.device_primary_identifier,
            "trigger_upper_limit": alert_payload.vital_range.upper_limit,
            "trigger_lower_limit": alert_payload.vital_range.lower_limit,
            "patient_id": str(patient.id),
            "patient_primary_identifier": str(patient.primary_identifier),
            "value_text": alert_payload.priority,
        },
        "previous_state": {},
        "event_type": event_class.event_type,
        "message_id": AnyUUID(),
        "event_data": {
            "code": alert_payload.code,
            "patient_id": str(patient.id),
            "patient_primary_identifier": str(patient.primary_identifier),
            "determination_time": alert_payload.determination_time.isoformat(),
            "value_text": alert_payload.priority,
            "device_primary_identifier": alert_payload.device_primary_identifier,
            "trigger_upper_limit": alert_payload.vital_range.upper_limit,
            "trigger_lower_limit": alert_payload.vital_range.lower_limit,
            "device_code": alert_payload.device_code,
            "active": alert_payload.active,
        },
        "entity_name": "patient",
        "emitted_by": "patient",
    }


@pytest.mark.asyncio
async def test_start_patient_encounter(async_db_session, producer_mock):
    patient = PatientFactory.build()
    async_db_session.add(patient)
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()

    patient_payload = SDCPatientPayloadFactory.build(primary_identifier=patient.primary_identifier)
    device_payload = SDCDevicePayloadFactory.build(primary_identifier=device.primary_identifier)
    device_discovered_payload = SDCDeviceDiscoveredPayloadFactory.build(
        patient=patient_payload, device=device_payload
    )
    sdc_message: SDCDeviceDiscoveredEvent = SDCDeviceDiscoveredEventFactory.build(
        payload=device_discovered_payload
    )
    broker_message = BrokerMessageFactory.build(value=sdc_message.model_dump_json())

    await start_patient_encounter(async_db_session, broker_message)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter = result.scalars().one()

    assert encounter
    assert str(encounter.subject_id) == patient.id
    assert encounter.device_id == device.id
    assert encounter.start_time == AnyDateTime()
    assert encounter.status is EncounterStatus.IN_PROGRESS
    assert encounter.end_time is None

    audit_log_message_sent = producer_mock.send_and_wait.call_args_list[-1][1]
    actual_topic = audit_log_message_sent["topic"]
    actual_headers = audit_log_message_sent["headers"]
    actual_value = json.loads(audit_log_message_sent["value"])
    assert actual_topic == config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    assert actual_headers == [("event_type", StartPatientEncounter.event_type.encode())]
    assert actual_value == {
        "entity_id": str(patient.id),
        "event_name": StartPatientEncounter.display_name,
        "performed_on": AnyDateTime(),
        "performed_by": "system",
        "event_state": {
            "id": AnyUUID(),
            "status": EncounterStatus.IN_PROGRESS.value,
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(),
            "end_time": None,
            "device": device.as_dict(),
            "patient": patient.as_dict(),
        },
        "previous_state": {},
        "event_type": StartPatientEncounter.event_type,
        "message_id": AnyUUID(),
        "event_data": {},
        "entity_name": "patient",
        "emitted_by": "patient",
    }


@pytest.mark.asyncio
async def test_start_patient_encounter_existing_encounter_same_patient_and_device(
    async_db_session, producer_mock
):
    initial_encounter_status = EncounterStatus.PLANNED
    patient = PatientFactory.build()
    async_db_session.add(patient)
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()
    encounter = EncounterFactory.build(
        device=device,
        subject=patient,
        status=initial_encounter_status,
    )
    async_db_session.add(encounter)
    await async_db_session.flush()

    patient_payload = SDCPatientPayloadFactory.build(primary_identifier=patient.primary_identifier)
    device_payload = SDCDevicePayloadFactory.build(primary_identifier=device.primary_identifier)
    device_discovered_payload = SDCDeviceDiscoveredPayloadFactory.build(
        patient=patient_payload, device=device_payload
    )
    sdc_message: SDCDeviceDiscoveredEvent = SDCDeviceDiscoveredEventFactory.build(
        payload=device_discovered_payload
    )
    broker_message = BrokerMessageFactory.build(value=sdc_message.model_dump_json())

    await start_patient_encounter(async_db_session, broker_message)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter = result.scalars().one()

    assert encounter
    assert str(encounter.subject_id) == patient.id
    assert encounter.device_id == device.id
    assert encounter.start_time == AnyDateTime()
    assert encounter.status is EncounterStatus.IN_PROGRESS
    assert encounter.end_time is None

    audit_log_message_sent = producer_mock.send_and_wait.call_args_list[-1][1]
    actual_topic = audit_log_message_sent["topic"]
    actual_headers = audit_log_message_sent["headers"]
    actual_value = json.loads(audit_log_message_sent["value"])
    assert actual_topic == config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    assert actual_headers == [("event_type", StartPatientEncounter.event_type.encode())]
    assert actual_value == {
        "entity_id": str(patient.id),
        "event_name": StartPatientEncounter.display_name,
        "performed_on": AnyDateTime(),
        "performed_by": "system",
        "event_state": {
            "id": AnyUUID(),
            "status": EncounterStatus.IN_PROGRESS.value,
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(allow_empty=True),
            "end_time": AnyDateTime(allow_empty=True),
            "device": device.as_dict(),
            "patient": patient.as_dict(),
        },
        "previous_state": {
            "id": AnyUUID(),
            "status": initial_encounter_status,
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(allow_empty=True),
            "end_time": AnyDateTime(allow_empty=True),
            "device": device.as_dict(),
            "patient": patient.as_dict(),
        },
        "event_type": StartPatientEncounter.event_type,
        "message_id": AnyUUID(),
        "event_data": {},
        "entity_name": "patient",
        "emitted_by": "patient",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_encounter_status",
    [
        EncounterStatus.IN_PROGRESS,
        EncounterStatus.COMPLETED,
        EncounterStatus.CANCELLED,
    ],
)
async def test_start_patient_encounter_existing_encounter_same_patient_and_device(
    async_db_session, producer_mock, initial_encounter_status
):
    patient = PatientFactory.build()
    async_db_session.add(patient)
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()
    encounter = EncounterFactory.build(
        device=device,
        subject=patient,
        status=initial_encounter_status,
    )
    async_db_session.add(encounter)
    await async_db_session.flush()

    patient_payload = SDCPatientPayloadFactory.build(primary_identifier=patient.primary_identifier)
    device_payload = SDCDevicePayloadFactory.build(primary_identifier=device.primary_identifier)
    device_discovered_payload = SDCDeviceDiscoveredPayloadFactory.build(
        patient=patient_payload, device=device_payload
    )
    sdc_message: SDCDeviceDiscoveredEvent = SDCDeviceDiscoveredEventFactory.build(
        payload=device_discovered_payload
    )
    broker_message = BrokerMessageFactory.build(value=sdc_message.model_dump_json())

    await start_patient_encounter(async_db_session, broker_message)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter = result.scalars().one()

    assert encounter
    assert str(encounter.subject_id) == patient.id
    assert encounter.device_id == device.id
    assert encounter.start_time == AnyDateTime()
    assert encounter.status is EncounterStatus.IN_PROGRESS
    assert encounter.end_time is None

    audit_log_message_sent = producer_mock.send_and_wait.call_args_list[-1][1]
    actual_topic = audit_log_message_sent["topic"]
    actual_headers = audit_log_message_sent["headers"]
    actual_value = json.loads(audit_log_message_sent["value"])
    assert actual_topic == config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    assert actual_headers == [("event_type", StartPatientEncounter.event_type.encode())]
    assert actual_value == {
        "entity_id": str(patient.id),
        "event_name": StartPatientEncounter.display_name,
        "performed_on": AnyDateTime(),
        "performed_by": "system",
        "event_state": {
            "id": AnyUUID(),
            "status": EncounterStatus.IN_PROGRESS.value,
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(allow_empty=True),
            "end_time": AnyDateTime(allow_empty=True),
            "device": device.as_dict(),
            "patient": patient.as_dict(),
        },
        "previous_state": {},
        "event_type": StartPatientEncounter.event_type,
        "message_id": AnyUUID(),
        "event_data": {},
        "entity_name": "patient",
        "emitted_by": "patient",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_encounter_status",
    [
        EncounterStatus.PLANNED,
        EncounterStatus.IN_PROGRESS,
        EncounterStatus.COMPLETED,
        EncounterStatus.CANCELLED,
    ],
)
async def test_start_patient_encounter_existing_encounter_other_device(
    async_db_session, producer_mock, initial_encounter_status
):
    patient = PatientFactory.build()
    async_db_session.add(patient)
    device = DeviceFactory.build()
    device_other = DeviceFactory.build()
    async_db_session.add(device)
    async_db_session.add(device_other)
    await async_db_session.flush()
    encounter = EncounterFactory.build(
        device=device_other,
        subject=patient,
        status=initial_encounter_status,
    )
    async_db_session.add(encounter)
    await async_db_session.flush()

    patient_payload = SDCPatientPayloadFactory.build(primary_identifier=patient.primary_identifier)
    device_payload = SDCDevicePayloadFactory.build(primary_identifier=device.primary_identifier)
    device_discovered_payload = SDCDeviceDiscoveredPayloadFactory.build(
        patient=patient_payload, device=device_payload
    )
    sdc_message: SDCDeviceDiscoveredEvent = SDCDeviceDiscoveredEventFactory.build(
        payload=device_discovered_payload
    )
    broker_message = BrokerMessageFactory.build(value=sdc_message.model_dump_json())

    await start_patient_encounter(async_db_session, broker_message)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter = result.scalars().one()

    assert encounter
    assert str(encounter.subject_id) == patient.id
    assert encounter.device_id == device.id
    assert encounter.start_time == AnyDateTime()
    assert encounter.status is EncounterStatus.IN_PROGRESS
    assert encounter.end_time is None

    audit_log_message_sent = producer_mock.send_and_wait.call_args_list[-1][1]
    actual_topic = audit_log_message_sent["topic"]
    actual_headers = audit_log_message_sent["headers"]
    actual_value = json.loads(audit_log_message_sent["value"])
    assert actual_topic == config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    assert actual_headers == [("event_type", StartPatientEncounter.event_type.encode())]
    assert actual_value == {
        "entity_id": str(patient.id),
        "event_name": StartPatientEncounter.display_name,
        "performed_on": AnyDateTime(),
        "performed_by": "system",
        "event_state": {
            "id": AnyUUID(),
            "status": EncounterStatus.IN_PROGRESS.value,
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(allow_empty=True),
            "end_time": AnyDateTime(allow_empty=True),
            "device": device.as_dict(),
            "patient": patient.as_dict(),
        },
        "previous_state": {},
        "event_type": StartPatientEncounter.event_type,
        "message_id": AnyUUID(),
        "event_data": {},
        "entity_name": "patient",
        "emitted_by": "patient",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_encounter_status",
    [
        EncounterStatus.PLANNED,
        EncounterStatus.IN_PROGRESS,
        EncounterStatus.COMPLETED,
        EncounterStatus.CANCELLED,
    ],
)
async def test_start_patient_encounter_existing_encounter_other_patient(
    async_db_session, producer_mock, initial_encounter_status
):
    patient = PatientFactory.build(id=uuid.uuid4())
    patient_other = PatientFactory.build(id=uuid.uuid4())
    async_db_session.add(patient)
    async_db_session.add(patient_other)
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()
    encounter = EncounterFactory.build(
        device=device,
        subject=patient_other,
        status=initial_encounter_status,
    )
    async_db_session.add(encounter)
    await async_db_session.flush()

    patient_payload = SDCPatientPayloadFactory.build(primary_identifier=patient.primary_identifier)
    device_payload = SDCDevicePayloadFactory.build(primary_identifier=device.primary_identifier)
    device_discovered_payload = SDCDeviceDiscoveredPayloadFactory.build(
        patient=patient_payload, device=device_payload
    )
    sdc_message: SDCDeviceDiscoveredEvent = SDCDeviceDiscoveredEventFactory.build(
        payload=device_discovered_payload
    )
    broker_message = BrokerMessageFactory.build(value=sdc_message.model_dump_json())

    await start_patient_encounter(async_db_session, broker_message)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter = result.scalars().one()

    assert encounter
    assert encounter.subject_id == patient.id
    assert encounter.device_id == device.id
    assert encounter.start_time == AnyDateTime()
    assert encounter.status is EncounterStatus.IN_PROGRESS
    assert encounter.end_time is None

    audit_log_message_sent = producer_mock.send_and_wait.call_args_list[-1][1]
    actual_topic = audit_log_message_sent["topic"]
    actual_headers = audit_log_message_sent["headers"]
    actual_value = json.loads(audit_log_message_sent["value"])
    assert actual_topic == config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    assert actual_headers == [("event_type", StartPatientEncounter.event_type.encode())]
    assert actual_value == {
        "entity_id": str(patient.id),
        "event_name": StartPatientEncounter.display_name,
        "performed_on": AnyDateTime(),
        "performed_by": "system",
        "event_state": {
            "id": AnyUUID(),
            "status": EncounterStatus.IN_PROGRESS.value,
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(allow_empty=True),
            "end_time": AnyDateTime(allow_empty=True),
            "device": device.as_dict(),
            "patient": patient.as_dict(),
        },
        "previous_state": {},
        "event_type": StartPatientEncounter.event_type,
        "message_id": AnyUUID(),
        "event_data": {},
        "entity_name": "patient",
        "emitted_by": "patient",
    }


@pytest.mark.asyncio
async def test_start_patient_encounter_no_patient(async_db_session, producer_mock):
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()

    device_payload = SDCDevicePayloadFactory.build(primary_identifier=device.primary_identifier)
    device_discovered_payload = SDCDeviceDiscoveredPayloadFactory.build(
        patient=None, device=device_payload
    )
    sdc_message: SDCDeviceDiscoveredEvent = SDCDeviceDiscoveredEventFactory.build(
        payload=device_discovered_payload
    )
    broker_message = BrokerMessageFactory.build(value=sdc_message.model_dump_json())

    await start_patient_encounter(async_db_session, broker_message)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter = result.scalars().one_or_none()

    assert not encounter
    audit_log_message_sent = producer_mock.send_and_wait.call_args_list
    assert not audit_log_message_sent


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_encounter_status",
    [
        EncounterStatus.PLANNED,
        EncounterStatus.IN_PROGRESS,
        EncounterStatus.COMPLETED,
        EncounterStatus.CANCELLED,
    ],
)
async def test_process_patient_session_ended_event_for_patient(
    async_db_session, producer_mock, initial_encounter_status
):
    patient = PatientFactory.build()
    async_db_session.add(patient)
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()
    encounter = EncounterFactory.build(
        device=device,
        subject=patient,
        status=initial_encounter_status,
        start_time=datetime(2024, 10, 10),
        end_time=None,
    )
    async_db_session.add(encounter)
    await async_db_session.flush()
    payload = SDCPatientSessionClosedPayloadFactory.build(
        patient_primary_identifier=patient.primary_identifier,
        device_primary_identifier=device.primary_identifier,
    )
    value = SDCPatientSessionClosedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=value.model_dump_json())

    await process_patient_session_ended_event_for_patient(async_db_session, broker_message)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter_found = result.scalars().one_or_none()
    assert not encounter_found

    audit_log_message_sent = producer_mock.send_and_wait.call_args_list[-1][1]
    actual_topic = audit_log_message_sent["topic"]
    actual_headers = audit_log_message_sent["headers"]
    actual_value = json.loads(audit_log_message_sent["value"])
    assert actual_topic == config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    assert actual_headers == [("event_type", CompletePatientEncounter.event_type.encode())]
    expected = {
        "entity_id": str(patient.id),
        "event_name": CompletePatientEncounter.display_name,
        "performed_on": AnyDateTime(),
        "performed_by": "system",
        "event_state": {
            "id": AnyUUID(),
            "status": EncounterStatus.COMPLETED.value,
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(),
            "end_time": AnyDateTime(),
            "device": device.as_dict(),
            "patient": patient.as_dict(),
        },
        "previous_state": {
            "id": AnyUUID(),
            "status": initial_encounter_status.value,
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(),
            "end_time": None,
            "device": device.as_dict(),
            "patient": patient.as_dict(),
        },
        "event_type": CompletePatientEncounter.event_type,
        "message_id": AnyUUID(),
        "event_data": {},
        "entity_name": "patient",
        "emitted_by": "patient",
    }
    assert actual_value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_encounter_status",
    [
        EncounterStatus.PLANNED,
        EncounterStatus.IN_PROGRESS,
        EncounterStatus.COMPLETED,
        EncounterStatus.CANCELLED,
    ],
)
async def test_process_patient_session_ended_event_for_patient(
    async_db_session, producer_mock, initial_encounter_status
):
    patient = PatientFactory.build()
    async_db_session.add(patient)
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()
    encounter = EncounterFactory.build(
        device=device,
        subject=patient,
        status=initial_encounter_status,
        start_time=datetime(2024, 10, 10),
        end_time=None,
    )
    async_db_session.add(encounter)
    await async_db_session.flush()
    payload = SDCPatientSessionClosedPayloadFactory.build(
        patient_primary_identifier=patient.primary_identifier,
        device_primary_identifier=device.primary_identifier,
    )
    value = SDCPatientSessionClosedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=value.model_dump_json())

    await process_patient_session_ended_event_for_patient(async_db_session, broker_message)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter_found = result.scalars().one_or_none()
    assert not encounter_found

    audit_log_message_sent = producer_mock.send_and_wait.call_args_list[-1][1]
    actual_topic = audit_log_message_sent["topic"]
    actual_headers = audit_log_message_sent["headers"]
    actual_value = json.loads(audit_log_message_sent["value"])
    assert actual_topic == config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    assert actual_headers == [("event_type", CompletePatientEncounter.event_type.encode())]
    expected = {
        "entity_id": str(patient.id),
        "event_name": CompletePatientEncounter.display_name,
        "performed_on": AnyDateTime(),
        "performed_by": "system",
        "event_state": {
            "id": AnyUUID(),
            "status": EncounterStatus.COMPLETED.value,
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(),
            "end_time": AnyDateTime(),
            "device": device.as_dict(),
            "patient": patient.as_dict(),
        },
        "previous_state": {
            "id": AnyUUID(),
            "status": initial_encounter_status.value,
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(),
            "end_time": None,
            "device": device.as_dict(),
            "patient": patient.as_dict(),
        },
        "event_type": CompletePatientEncounter.event_type,
        "message_id": AnyUUID(),
        "event_data": {},
        "entity_name": "patient",
        "emitted_by": "patient",
    }
    assert actual_value == expected


@pytest.mark.asyncio
async def test_process_patient_session_ended_event_for_patient_no_patient_in_payload(
    async_db_session, producer_mock
):
    patient = PatientFactory.build()
    async_db_session.add(patient)
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()
    encounter = EncounterFactory.build(
        device=device,
        subject=patient,
        status=EncounterStatus.IN_PROGRESS,
        start_time=datetime(2024, 10, 10),
    )
    async_db_session.add(encounter)
    await async_db_session.flush()
    payload = SDCPatientSessionClosedPayloadFactory.build(
        device_primary_identifier=device.primary_identifier,
    )
    value = SDCPatientSessionClosedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=value.model_dump_json())

    await process_patient_session_ended_event_for_patient(async_db_session, broker_message)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter_found = result.scalars().all()
    assert not encounter_found


@pytest.mark.asyncio
async def test_process_patient_session_ended_event_for_patient_patient_doesnt_exist(
    async_db_session, producer_mock
):
    await async_db_session.flush()
    payload = SDCPatientSessionClosedPayloadFactory.build(
        device_primary_identifier="PM-001",
    )
    value = SDCPatientSessionClosedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=value.model_dump_json())

    await process_patient_session_ended_event_for_patient(async_db_session, broker_message)

    audit_calls = producer_mock.send_and_wait.call_args_list
    assert not audit_calls


@pytest.mark.asyncio
async def test_process_patient_session_ended_event_for_patient_encounter_doesnt_exist(
    async_db_session, producer_mock
):
    patient = PatientFactory.build()
    async_db_session.add(patient)
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()

    await async_db_session.flush()
    payload = SDCPatientSessionClosedPayloadFactory.build(
        device_primary_identifier=device.primary_identifier,
        patient_primary_identifier=patient.primary_identifier,
    )
    value = SDCPatientSessionClosedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=value.model_dump_json())

    await process_patient_session_ended_event_for_patient(async_db_session, broker_message)

    audit_calls = producer_mock.send_and_wait.call_args_list
    assert not audit_calls


@pytest.mark.asyncio
async def test_process_patient_session_started_event(async_db_session, producer_mock):
    patient_identifier = "PX-001"
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()
    alert_1 = SDCAlertPayloadFactory.build(
        patient_primary_identifier=patient_identifier,
    )
    alert_2 = SDCAlertPayloadFactory.build(
        patient_primary_identifier=patient_identifier,
    )
    patient_payload = SDCPatientPayloadFactory.build(
        primary_identifier=patient_identifier, alerts=[alert_1, alert_2]
    )
    payload = SDCPatientSessionStartedPayloadFactory.build(
        patient_monitor_identifier=device.primary_identifier, patient=patient_payload
    )
    event = SDCPatientSessionStartedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_patient_session_started_event(async_db_session, broker_message)

    stmt = select(Patient)
    result = await async_db_session.execute(stmt)
    patient_found = result.scalars().one()

    assert patient_found.primary_identifier == patient_identifier
    assert patient_found.given_name == patient_payload.given_name_decrypted
    assert patient_found.family_name == patient_payload.family_name_decrypted
    assert patient_found.gender == patient_payload.gender
    assert patient_found.birth_date == patient_payload.birth_date_decrypted

    stmt = select(Observation)
    result = await async_db_session.execute(stmt)
    observations_found = result.scalars().all()
    assert len(observations_found) == len(patient_payload.alerts)

    stmt = select(AlertLog)
    result = await async_db_session.execute(stmt)
    phy_alerts_found = result.scalars().all()
    assert len(phy_alerts_found) == len(patient_payload.alerts)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter_found = result.scalars().one()
    assert encounter_found.status == EncounterStatus.IN_PROGRESS
    assert encounter_found.start_time == AnyDateTime()
    assert encounter_found.created_at == AnyDateTime()
    assert encounter_found.end_time is None


@pytest.mark.asyncio
async def test_process_patient_admission_rejected_event(async_db_session, producer_mock):
    patient = PatientFactory.build()
    async_db_session.add(patient)
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()
    encounter = EncounterFactory.build(
        device=device,
        subject=patient,
        status=EncounterStatus.IN_PROGRESS,
        start_time=datetime(2024, 10, 10),
    )
    async_db_session.add(encounter)
    await async_db_session.flush()
    payload = SDCPatientAdmissionRejectedPayloadFactory.build(
        device_primary_identifier=device.primary_identifier,
        patient_primary_identifier=patient.primary_identifier,
    )
    value = SDCPatientAdmissionRejectedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=value.model_dump_json())

    await process_patient_admission_rejected(async_db_session, broker_message)

    stmt = select(Encounter)
    result = await async_db_session.execute(stmt)
    encounter_found = result.scalars().one_or_none()
    assert encounter_found
    assert encounter_found.status == EncounterStatus.CANCELLED
