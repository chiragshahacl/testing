from cache import remove_cache
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.alerts.repository import AlertsLogRepository
from app.alerts.stream import AlertLogEventStream
from app.event_processing.subscriber import BrokerMessage
from app.event_processing.topics.alerts.schemas import SDCNewAlertEvent
from app.event_processing.topics.events_sdc.schemas import SDCAlertPayload
from app.patient.events import (
    ActivateAlertEvent,
    CreateObservationEvent,
    DeactivateAlertEvent,
    DeleteObservationEvent,
)
from app.patient.repository import ReadPatientRepository
from app.patient.schemas import (
    CreateObservationSchema,
)
from app.patient.stream import ObservationEventStream
from app.settings import config


async def process_alert_found(db_session: AsyncSession, incoming_alert: SDCAlertPayload):
    if not incoming_alert.is_backfill:
        event_stream = ObservationEventStream(db_session)
        patient = await ReadPatientRepository(db_session).get_patient_by_identifier(
            incoming_alert.patient_primary_identifier
        )
        if not patient:
            logger.error(
                "Patient with identifier "
                f"{incoming_alert.patient_primary_identifier}"
                "does not exist"
            )
            return None

        alerts_found = await ReadPatientRepository(db_session).get_alerts(
            incoming_alert.device_code, patient.id, incoming_alert.code
        )

        if incoming_alert.active:
            if not alerts_found:
                logger.info(f"Alert {incoming_alert.code} is now active")
                payload = CreateObservationSchema(
                    code=incoming_alert.code,
                    subject_id=patient.id,
                    effective_dt=incoming_alert.determination_time,
                    value_text=incoming_alert.priority,
                    device_code=incoming_alert.device_code,
                    device_primary_identifier=incoming_alert.device_primary_identifier,
                    is_alert=True,
                )
                event = CreateObservationEvent("system", payload)
                await event_stream.add(event, None)
        else:
            logger.info(f"Alert {incoming_alert.code} is now inactive")
            events = [
                (DeleteObservationEvent(username="system"), observation)
                for observation in alerts_found
            ]
            await event_stream.batch_delete(events)
    else:
        logger.info("Ignoring backfilled alert")


@remove_cache("Observation")
async def process_physiological_incoming_alert_event(
    db_session: AsyncSession, message: BrokerMessage
) -> None:
    logger.info("Processing new alert event")
    if message.source_topic == config.EVENTS_ALERT_TOPIC:
        incoming_alert = SDCNewAlertEvent.model_validate_json(message.value)
        await process_alert_found(db_session, incoming_alert.payload)


@remove_cache("observation-audit")
async def insert_alert_state_in_audit_log(db_session: AsyncSession, message: BrokerMessage) -> None:
    incoming_alert = SDCNewAlertEvent.model_validate_json(message.value).payload
    await process_alert_found_audit_log(db_session, incoming_alert)


async def process_alert_found_audit_log(db_session: AsyncSession, incoming_alert: SDCAlertPayload):
    alert_repo = AlertsLogRepository(db_session)
    patient = await ReadPatientRepository(db_session).get_patient_by_identifier(
        incoming_alert.patient_primary_identifier
    )
    if not patient:
        logger.warning("Alert triggered for non existing patient")
        return

    alert = await alert_repo.get(
        patient.id,
        incoming_alert.device_primary_identifier,
        incoming_alert.code,
        incoming_alert.determination_time,
    )

    # When an alert is latching is considered disabled for the purpose of creating an audit log
    incoming_alert_active = incoming_alert.active and not incoming_alert.latching

    stream = AlertLogEventStream(db_session)
    if alert and alert.active != incoming_alert_active:
        logger.warning("Alert activated and deactivated at the same time")
        logger.warning(f"Found alert: {alert}")
        return

    if not alert and incoming_alert_active:
        logger.info("Alert not found, creating it.")
        event = ActivateAlertEvent(
            "system",
            incoming_alert.code,
            patient,
            incoming_alert.determination_time,
            incoming_alert.priority,
            incoming_alert.device_primary_identifier,
            incoming_alert.device_code,
            incoming_alert.vital_range.upper_limit if incoming_alert.vital_range else None,
            incoming_alert.vital_range.lower_limit if incoming_alert.vital_range else None,
        )
        await stream.add(event, entity=alert, related_entity_id=patient.id)
    elif not alert and not incoming_alert_active:
        logger.info("Deactivating alert")
        event = DeactivateAlertEvent(
            "system",
            incoming_alert.code,
            patient,
            incoming_alert.determination_time,
            incoming_alert.priority,
            incoming_alert.device_primary_identifier,
            incoming_alert.device_code,
            incoming_alert.vital_range.upper_limit if incoming_alert.vital_range else None,
            incoming_alert.vital_range.lower_limit if incoming_alert.vital_range else None,
        )
        await stream.add(event, entity=alert, related_entity_id=patient.id)
