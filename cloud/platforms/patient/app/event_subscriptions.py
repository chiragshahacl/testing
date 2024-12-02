from app.event_processing.adapters import DatabaseAdapter
from app.event_processing.subscriber import EventSubscriber, HeaderEventTypes
from app.event_processing.topics.alerts import processors as alert_processors
from app.event_processing.topics.events_sdc import processors as sdc_processors


def register_event_subscriptions():
    event_subscriber = EventSubscriber()
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.ALERT_OBSERVATION_EVENT,
        DatabaseAdapter(alert_processors.process_physiological_incoming_alert_event),
    )
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.ALERT_OBSERVATION_EVENT,
        DatabaseAdapter(alert_processors.insert_alert_state_in_audit_log),
    )
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.DEVICE_DISCOVERED_EVENT,
        DatabaseAdapter(sdc_processors.process_device_discovered_event),
    )

    event_subscriber.register_event_type_handler(
        HeaderEventTypes.PATIENT_SESSION_CLOSED_EVENT,
        DatabaseAdapter(sdc_processors.clean_alert_state_audit_log_when_subject_is_removed),
    )
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.PATIENT_SESSION_CLOSED_EVENT,
        DatabaseAdapter(sdc_processors.process_patient_session_closed_event),
    )

    event_subscriber.register_event_type_handler(
        HeaderEventTypes.SENSOR_REMOVED_EVENT,
        DatabaseAdapter(sdc_processors.process_sensor_removed_event_for_patient),
    )
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.ALERT_OBSERVATION_EVENT,
        DatabaseAdapter(sdc_processors.process_technical_alerts),
    )
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.SENSOR_REMOVED_EVENT,
        DatabaseAdapter(sdc_processors.process_sensor_removed_event_for_device),
    )
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.DEVICE_NEW_VITALS_RANGES,
        DatabaseAdapter(sdc_processors.process_device_vital_range_message),
    )
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.PM_CONFIGURATION_UPDATED,
        DatabaseAdapter(sdc_processors.process_updated_pm_config),
    )
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.PATIENT_SESSION_STARTED,
        DatabaseAdapter(sdc_processors.process_patient_session_started_event),
    )
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.PATIENT_ADMISSION_REJECTED,
        DatabaseAdapter(sdc_processors.process_patient_admission_rejected),
    )
