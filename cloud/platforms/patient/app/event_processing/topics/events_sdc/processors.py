import uuid
from typing import Sequence

import cache
from cache import remove_cache
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.alerts.repository import AlertsLogRepository, ObservationRepository
from app.common.models import Observation, Patient
from app.device.src.common.event_sourcing.events import (
    BackfillDeviceVitalRangeEvent,
    CreateVitalRangeEvent,
    DeleteDeviceEvent,
    DeleteVitalRangeEvent,
    UpdateDeviceConfigEvent,
)
from app.device.src.common.event_sourcing.stream import (
    DeviceEventStream,
    VitalRangeEventStream,
)
from app.device.src.consumer import (
    create_or_update_discovered_device,
    process_alert_payload,
)
from app.device.src.device.repository import DeviceAlertRepository, ReadDeviceRepository
from app.device.src.device.schemas import CreateVitalRangeSchema, UpdateDeviceSchema
from app.encounter.repository import ReadEncounterRepository
from app.encounter.services import EncounterService
from app.encounter.streams import EncounterEventStream
from app.event_processing.subscriber import BrokerMessage
from app.event_processing.topics.alerts.processors import (
    process_alert_found_audit_log,
)
from app.event_processing.topics.alerts.schemas import SDCNewAlertEvent
from app.event_processing.topics.events_sdc.schemas import (
    SDCAlertPayload,
    SDCDeviceDiscoveredEvent,
    SDCNewVitalsRangesEvent,
    SDCPatientAdmissionEvent,
    SDCPatientMonitorConfigurationUpdatedEvent,
    SDCPatientPayload,
    SDCPatientSessionClosedEvent,
    SDCPatientSessionStartedEvent,
    SDCSensorRemovedEvent,
)
from app.patient.events import (
    CreatePatientEvent,
    DeleteObservationEvent,
    MultipleObservationsUpdatedEvent,
    UpdatePatientInfoEvent,
)
from app.patient.repository import ReadPatientRepository
from app.patient.schemas import (
    CreatePatientSchema,
    UpdatePatientSchema,
)
from app.patient.stream import ObservationEventStream, PatientEventStream
from app.settings import config


class StateAdapter:
    def __init__(self):
        self.username = config.SYSTEM_USERNAME


class RequestAdapter:
    def __init__(self):
        self.state = StateAdapter()


@remove_cache("Bed")
async def start_patient_encounter(db_session: AsyncSession, message: BrokerMessage) -> None:
    device_discovered_event = SDCDeviceDiscoveredEvent.model_validate_json(message.value)
    if not device_discovered_event.payload.device.gateway_id:
        read_encounter_repository = ReadEncounterRepository(db_session)
        read_patient_repository = ReadPatientRepository(db_session)
        read_device_repository = ReadDeviceRepository(db_session)
        encounter_event_stream = EncounterEventStream(db_session)
        encounter_service = EncounterService(
            RequestAdapter(),
            encounter_event_stream,
            read_encounter_repository,
            read_patient_repository,
            read_device_repository,
        )
        if device_discovered_event.payload.patient:
            device_payload = device_discovered_event.payload.device
            patient_payload = device_discovered_event.payload.patient
            logger.info(f"Starting encounter for patient: {patient_payload.primary_identifier}")
            encounter = await encounter_service.start_encounter_by_identifiers(
                patient_payload.primary_identifier, device_payload.primary_identifier
            )
            logger.info(f"Encounter created with status: {encounter.status}")


async def reject_patient_encounter(db_session: AsyncSession, message: BrokerMessage) -> None:
    patient_admission_rejected_event = SDCPatientAdmissionEvent.model_validate_json(message.value)
    read_patient_repository = ReadPatientRepository(db_session)
    read_device_repository = ReadDeviceRepository(db_session)
    read_encounter_repository = ReadEncounterRepository(db_session)
    encounter_event_stream = EncounterEventStream(db_session)
    encounter_service = EncounterService(
        RequestAdapter(),
        encounter_event_stream,
        read_encounter_repository,
        read_patient_repository,
        read_device_repository,
    )
    await encounter_service.cancel_encounter_by_identifiers(
        patient_admission_rejected_event.payload.patient_primary_identifier,
        patient_admission_rejected_event.payload.device_primary_identifier,
    )


async def create_or_update_patient(
    db_session: AsyncSession, patient_data: SDCPatientPayload, device_primary_identifier: str
) -> None:
    event_stream = PatientEventStream(db_session)
    patient = await ReadPatientRepository(db_session).get_patient_by_identifier(
        patient_data.primary_identifier
    )
    if patient:
        logger.info("Patient found")
        payload = UpdatePatientSchema(
            id=patient.id,
            active=patient.active,
            primary_identifier=patient_data.primary_identifier,
            given_name=patient_data.given_name_decrypted,
            family_name=patient_data.family_name_decrypted,
            gender=patient_data.gender,
            birth_date=patient_data.birth_date_decrypted,
        )
        event = UpdatePatientInfoEvent("system", payload)
        patient = await event_stream.add(event, patient)
    else:
        logger.info("Patient not found, creating")
        payload = CreatePatientSchema(
            primary_identifier=patient_data.primary_identifier,
            given_name=patient_data.given_name_decrypted,
            family_name=patient_data.family_name_decrypted,
            gender=patient_data.gender,
            birth_date=patient_data.birth_date_decrypted,
            active=True,
        )
        event = CreatePatientEvent("system", payload)
        patient = await event_stream.add(event, None)

    await process_patient_alerts(
        db_session, device_primary_identifier, patient, patient_data.alerts
    )

    for alert_payload in patient_data.alerts:
        await process_alert_found_audit_log(db_session, alert_payload)


async def process_patient_alerts(
    db_session: AsyncSession,
    device_primary_identifier: str,
    patient: Patient,
    alert_payloads: Sequence[SDCAlertPayload],
):
    observation_stream = ObservationEventStream(db_session)
    observation_repository = ObservationRepository(db_session)
    device_repository = ReadDeviceRepository(db_session)

    device = await device_repository.get_device_by_identifier(device_primary_identifier)

    def create_observation_from_alert_payload(payload: SDCAlertPayload) -> Observation:
        return Observation(
            id=uuid.uuid4(),
            category="vital-signs",  # TODO: WHY IS THE DEFAULT VITAL-SIGNS? THIS SHOULD BE ALERT
            code=payload.code,
            subject_id=patient.id,
            effective_dt=payload.determination_time,
            value_text=payload.priority,
            device_code=payload.device_code,
            device_primary_identifier=payload.device_primary_identifier,
            is_alert=True,
        )

    alerts_to_create = [
        create_observation_from_alert_payload(payload)
        for payload in alert_payloads
        if payload.active
    ]
    if alerts_to_create:
        await observation_repository.bulk_add_alerts(alerts_to_create)

    alerts_to_delete = [
        create_observation_from_alert_payload(payload)
        for payload in alert_payloads
        if not payload.active
    ]
    if alerts_to_delete:
        await observation_repository.bulk_delete_alerts(alerts_to_delete)

    await observation_stream.notify(
        MultipleObservationsUpdatedEvent(config.SYSTEM_USERNAME), device.id
    )


@remove_cache("Patient")
async def process_device_discovered_event_for_patient(
    db_session: AsyncSession, message: BrokerMessage
) -> None:
    logger.info("Processing device discovered event")
    device_discovered_event = SDCDeviceDiscoveredEvent.model_validate_json(message.value)
    patient_data = device_discovered_event.payload.patient
    device_primary_identifier = device_discovered_event.payload.device.primary_identifier
    if patient_data:
        await create_or_update_patient(db_session, patient_data, device_primary_identifier)
    else:
        logger.info("Ignoring device discovered with no patient data")


@remove_cache("observation-audit")
async def clean_alert_state_audit_log_when_subject_is_removed(
    db_session: AsyncSession, message: BrokerMessage
):
    payload = SDCPatientSessionClosedEvent.model_validate_json(message.value)
    patient = await ReadPatientRepository(db_session).get_patient_by_device_identifier(
        payload.payload.device_primary_identifier
    )

    if not patient:
        logger.warning("Session closed for non existing patient")
        return

    await AlertsLogRepository(db_session).delete_alerts_for_patient(patient.id)
    logger.info(f"Removed session alerts for patient: {patient.id} - {patient.primary_identifier}")


@remove_cache("Observation")
async def process_sensor_removed_event_for_patient(
    db_session: AsyncSession, message: BrokerMessage
) -> None:
    logger.info("Processing sensor removed event")
    event = SDCSensorRemovedEvent.model_validate_json(message.value)

    observation_found = await ReadPatientRepository(db_session).get_sensor_observations(
        device_primary_identifier=event.payload.device_primary_identifier
    )
    events = [
        (DeleteObservationEvent(username="system"), observation)
        for observation in observation_found
    ]
    await ObservationEventStream(db_session).batch_delete(events)


@cache.remove_cache("Device")
async def process_device_discovered_event_for_device(
    db_session: AsyncSession, message: BrokerMessage
):
    event = SDCDeviceDiscoveredEvent.model_validate_json(message.value)
    device_data = event.payload.device
    patient_identifier = event.payload.patient.primary_identifier if event.payload.patient else None
    repository = ReadDeviceRepository(db_session)
    device = await repository.get_device_by_identifier(device_data.primary_identifier)
    gateway = await repository.get_device_by_identifier(device_data.gateway_id)
    gateway_id = None if gateway is None else gateway.id
    await create_or_update_discovered_device(
        db_session, device, device_data, gateway_id, patient_identifier
    )


# pylint: disable=R0914,C0103
@cache.remove_cache("Device")
async def process_device_vital_range_message(db_session: AsyncSession, message: BrokerMessage):
    event_stream = VitalRangeEventStream(db_session)
    read_device_repo = ReadDeviceRepository(db_session)
    vital_range_data = SDCNewVitalsRangesEvent.model_validate_json(message.value)

    current_vital_ranges = await read_device_repo.get_device_vital_ranges_by_identifier(
        vital_range_data.payload.primary_identifier.lower()
    )

    vrs_to_create = []
    vrs_to_delete = []
    found_vital_ranges = {vr.code: vr for vr in current_vital_ranges}

    for incoming_vr in vital_range_data.payload.ranges:
        if not (existing_vr := found_vital_ranges.get(incoming_vr.code)):
            vrs_to_create.append(incoming_vr)
        else:
            if incoming_vr.is_backfill:
                logger.info("Ignoring because it is backfill")
                incoming_vr_event = BackfillDeviceVitalRangeEvent(config.SYSTEM_USERNAME)
                await event_stream.add(incoming_vr_event, incoming_vr)
            elif any(
                [
                    existing_vr.upper_limit != incoming_vr.upper_limit,
                    existing_vr.lower_limit != incoming_vr.lower_limit,
                    existing_vr.alert_condition_enabled != incoming_vr.alert_condition_enabled,
                ]
            ):
                vrs_to_delete.append(existing_vr)
                vrs_to_create.append(incoming_vr)
            else:
                logger.info("Ignoring unchanged vital range")

    if vrs_to_delete:
        delete_events = [
            (DeleteVitalRangeEvent(config.SYSTEM_USERNAME), vital_range)
            for vital_range in vrs_to_delete
        ]
        await event_stream.batch_delete(delete_events)

    device = await read_device_repo.get_device_by_identifier(
        vital_range_data.payload.primary_identifier
    )

    if not device:
        logger.warning(
            f"Trying to create vitals range for device"
            f" {vital_range_data.payload.primary_identifier}, which doesn't exist"
        )
        return

    create_events = []
    for vr in vrs_to_create:
        create_payload = CreateVitalRangeSchema(
            code=vr.code,
            upper_limit=vr.upper_limit,
            lower_limit=vr.lower_limit,
            device_id=device.id,
            alert_condition_enabled=vr.alert_condition_enabled,
        )
        create_events.append((CreateVitalRangeEvent(config.SYSTEM_USERNAME, create_payload), None))

    if create_events:
        await event_stream.batch_add(create_events)


@cache.remove_cache("Device")
async def process_technical_alerts(db_session: AsyncSession, message: BrokerMessage) -> None:
    if message.source_topic == config.EVENTS_SDC_TOPIC:
        event = SDCNewAlertEvent.model_validate_json(message.value)
        await process_alert_payload(db_session, event.payload)
    else:
        logger.debug("Not a technical alert")


@cache.remove_cache("Device")
async def process_sensor_removed_event_for_device(
    db_session: AsyncSession, message: BrokerMessage
) -> None:
    sensor_removed_event = SDCSensorRemovedEvent.model_validate_json(message.value)
    device_identifier = sensor_removed_event.payload.device_primary_identifier
    logger.info(f"Received sensor removed event: {device_identifier}")
    device = await ReadDeviceRepository(db_session).get_device_by_identifier(device_identifier)

    if not device:
        logger.warning(f"Device with identifier {device_identifier} does not exist")
        return

    if device.gateway_id is None:
        logger.warning("Tried to remove a patient monitor")
        return

    delete_device_event = DeleteDeviceEvent(config.SYSTEM_USERNAME)
    await DeviceEventStream(db_session).delete(
        delete_device_event,
        device,
        related_entity_id=sensor_removed_event.payload.patient_primary_identifier,
    )


@cache.remove_cache("Device")
async def process_patient_session_ended_event_for_device(
    db_session: AsyncSession, message: BrokerMessage
) -> None:
    event = SDCPatientSessionClosedEvent.model_validate_json(message.value)
    logger.info("Received patient session ended event")

    device_repository = ReadDeviceRepository(db_session)

    pm = await device_repository.get_device_by_identifier(event.payload.device_primary_identifier)
    if not pm:
        logger.warning(f"Patient Monitor not found: {event.payload.device_primary_identifier}")
        return

    sensors = await device_repository.get_gateway_sensors(pm.id)

    if not sensors:
        logger.info(f"No sensors found for PM: {event.payload.device_primary_identifier}")

    device_repository = DeviceAlertRepository(db_session)
    await device_repository.delete_alerts_by_device([sensor.id for sensor in sensors])
    logger.info("Removed sensor alerts")


@cache.remove_cache("Bed")
async def process_patient_session_ended_event_for_patient(
    db_session: AsyncSession, message: BrokerMessage
) -> None:
    event = SDCPatientSessionClosedEvent.model_validate_json(message.value)
    read_encounter_repository = ReadEncounterRepository(db_session)
    read_patient_repository = ReadPatientRepository(db_session)
    read_device_repository = ReadDeviceRepository(db_session)
    encounter_event_stream = EncounterEventStream(db_session)
    encounter_service = EncounterService(
        RequestAdapter(),
        encounter_event_stream,
        read_encounter_repository,
        read_patient_repository,
        read_device_repository,
    )

    patient = await read_patient_repository.get_patient_by_device_identifier(
        event.payload.device_primary_identifier
    )

    if not patient:
        logger.info("Ignoring event with no patient")
        return

    encounter = await read_encounter_repository.get_patient_encounter(patient.id)
    if not encounter:
        logger.warning(
            f"Encounter not found for patient: {event.payload.patient_primary_identifier}"
        )
        return
    await encounter_service.complete_encounter_by_patient_id(encounter.subject_id)


@cache.remove_cache("Device")
async def process_updated_pm_config(db_session: AsyncSession, message: BrokerMessage) -> None:
    event = SDCPatientMonitorConfigurationUpdatedEvent.model_validate_json(message.value)
    logger.info("Received patient monitor configuration updated event")

    device_repository = ReadDeviceRepository(db_session)

    if device := await device_repository.get_device_by_identifier(
        event.payload.device_primary_identifier
    ):
        event_stream = DeviceEventStream(db_session)
        event.payload = UpdateDeviceSchema(
            id=device.id,
            primary_identifier=event.payload.device_primary_identifier,
            name=device.name,
            gateway_id=device.gateway_id,
            subject_identifier=device.subject_identifier,
            model_number=device.model_number,
            audio_pause_enabled=event.payload.audio_pause_enabled,
            audio_enabled=event.payload.audio_enabled,
        )
        event = UpdateDeviceConfigEvent(
            config.SYSTEM_USERNAME,
            event.payload.audio_pause_enabled,
            event.payload.audio_enabled,
        )
        await event_stream.add(event, device)
    else:
        logger.warning(
            f"Device with identifier {event.payload.device_primary_identifier} does not exist"
        )


async def process_device_discovered_event(db_session: AsyncSession, message: BrokerMessage) -> None:
    await process_device_discovered_event_for_device(db_session, message)
    await process_device_discovered_event_for_patient(db_session, message)
    await start_patient_encounter(db_session, message)


async def process_patient_session_closed_event(
    db_session: AsyncSession, message: BrokerMessage
) -> None:
    await process_patient_session_ended_event_for_device(db_session, message)
    await process_patient_session_ended_event_for_patient(db_session, message)


@cache.remove_cache("Bed")
@cache.remove_cache("Patient")
@cache.remove_cache("Observation")
async def process_patient_session_started_event(
    db_session: AsyncSession, message: BrokerMessage
) -> None:
    event = SDCPatientSessionStartedEvent.model_validate_json(message.value)
    await create_or_update_patient(
        db_session, event.payload.patient, event.payload.patient_monitor_identifier
    )
    logger.info(f"Starting encounter for patient: {event.payload.patient.primary_identifier}")
    read_encounter_repository = ReadEncounterRepository(db_session)
    read_patient_repository = ReadPatientRepository(db_session)
    read_device_repository = ReadDeviceRepository(db_session)
    encounter_event_stream = EncounterEventStream(db_session)
    encounter_service = EncounterService(
        RequestAdapter(),
        encounter_event_stream,
        read_encounter_repository,
        read_patient_repository,
        read_device_repository,
    )
    await encounter_service.start_encounter_by_identifiers(
        event.payload.patient.primary_identifier, event.payload.patient_monitor_identifier
    )
    logger.info("Patient encounter started")


@cache.remove_cache("Bed")
async def process_patient_admission_rejected(
    db_session: AsyncSession, message: BrokerMessage
) -> None:
    await reject_patient_encounter(db_session, message)
