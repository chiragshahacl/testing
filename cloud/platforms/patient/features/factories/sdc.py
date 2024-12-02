import random
from datetime import datetime
from typing import Any, Dict, Type

from common_schemas.secret_string import RedactedDateString, RedactedString
from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from app.event_processing.topics.alerts.schemas import SDCNewAlertEvent
from app.event_processing.topics.events_sdc.schemas import (
    SDCAlertPayload,
    SDCDeviceConfigPayload,
    SDCDeviceDiscoveredEvent,
    SDCDeviceDiscoveredPayload,
    SDCDevicePayload,
    SDCIncomingMessage,
    SDCNewVitalsRangesEvent,
    SDCNewVitalsRangesPayload,
    SDCPatientAdmissionEvent,
    SDCPatientAdmissionRejectedPayload,
    SDCPatientMonitorConfigurationUpdatedEvent,
    SDCPatientMonitorConfigurationUpdatedPayload,
    SDCPatientPayload,
    SDCPatientSessionClosedEvent,
    SDCPatientSessionClosedPayload,
    SDCPatientSessionStartedEvent,
    SDCPatientSessionStartedPayload,
    SDCSensorPayload,
    SDCSensorRemovedEvent,
    SDCSensorRemovedPayload,
    SDCVitalsRange,
)


class SDCIncomingMessageFactory(ModelFactory[SDCIncomingMessage]):
    __model__ = SDCIncomingMessage
    __fake__ = Faker()


class SDCPatientSessionClosedPayloadFactory(ModelFactory[SDCPatientSessionClosedPayload]):
    __model__ = SDCPatientSessionClosedPayload
    __fake__ = Faker()


class SDCPatientSessionClosedEventFactory(ModelFactory[SDCPatientSessionClosedEvent]):
    __model__ = SDCPatientSessionClosedEvent
    __fake__ = Faker()


class SDCSensorRemovedPayloadFactory(ModelFactory[SDCSensorRemovedPayload]):
    __model__ = SDCSensorRemovedPayload
    __fake__ = Faker()

    determination_time = lambda: datetime.now().isoformat()


class SDCSensorRemovedEventFactory(ModelFactory[SDCSensorRemovedEvent]):
    __model__ = SDCSensorRemovedEvent
    __fake__ = Faker()


class SDCPatientPayloadFactory(ModelFactory[SDCPatientPayload]):
    __model__ = SDCPatientPayload
    __fake__ = Faker()

    alerts = lambda: []

    @classmethod
    def get_provider_map(cls) -> Dict[Type, Any]:
        providers_map = super().get_provider_map()
        return {
            RedactedString: lambda: RedactedString(Faker().name()),
            RedactedDateString: lambda: RedactedDateString(str(Faker().date())),
            **providers_map,
        }


class SDCDeviceConfigPayloadFactory(ModelFactory[SDCDeviceConfigPayload]):
    __model__ = SDCDeviceConfigPayload
    __fake__ = Faker()

    audio_enabled = lambda: False
    audio_pause_enabled = lambda: True


class SDCSensorPayloadFactory(ModelFactory[SDCSensorPayload]):
    __model__ = SDCSensorPayload
    __fake__ = Faker()


class SDCDevicePayloadFactory(ModelFactory[SDCDevicePayload]):
    __model__ = SDCDevicePayload
    __fake__ = Faker()

    connected_sensors = lambda: []
    alerts = lambda: []
    config = SDCDeviceConfigPayloadFactory
    gateway_id = lambda: None


class SDCDeviceDiscoveredPayloadFactory(ModelFactory[SDCDeviceDiscoveredPayload]):
    __model__ = SDCDeviceDiscoveredPayload
    __fake__ = Faker()

    device = SDCDevicePayloadFactory
    patient = SDCPatientPayloadFactory


class SDCDeviceDiscoveredEventFactory(ModelFactory[SDCDeviceDiscoveredEvent]):
    __model__ = SDCDeviceDiscoveredEvent
    __fake__ = Faker()

    payload = SDCDeviceDiscoveredPayloadFactory


class SDCAlertPayloadFactory(ModelFactory[SDCAlertPayload]):
    __model__ = SDCAlertPayload
    __fake__ = Faker()

    device_code = lambda: Faker().bothify(text="device_code_???###", letters="ABCDE")
    is_backfill = lambda: False
    determination_time = lambda: datetime.now().isoformat()
    active = lambda: True
    latching = lambda: False
    vital_range = lambda: SDCVitalsRangeFactory.build()


class SDCNewAlertEventFactory(ModelFactory[SDCNewAlertEvent]):
    __model__ = SDCNewAlertEvent
    __fake__ = Faker()

    payload = SDCAlertPayloadFactory


class SDCVitalsRangeFactory(ModelFactory[SDCVitalsRange]):
    __model__ = SDCVitalsRange
    __fake__ = Faker()

    code = lambda: str(random.randrange(1000, 2000))
    lower_limit = lambda: 80.00
    upper_limit = lambda: 100.00
    alert_condition_enabled = lambda: False
    is_backfill = False


class SDCNewVitalsRangesPayloadFactory(ModelFactory[SDCNewVitalsRangesPayload]):
    __model__ = SDCNewVitalsRangesPayload
    __fake__ = Faker()

    ranges = lambda: [SDCVitalsRangeFactory.build() for _ in range(2)]


class SDCNewVitalsRangesEventFactory(ModelFactory[SDCNewVitalsRangesEvent]):
    __model__ = SDCNewVitalsRangesEvent
    __fake__ = Faker()

    payload = SDCNewVitalsRangesPayloadFactory


class SDCPatientMonitorConfigurationUpdatedPayloadFactory(
    ModelFactory[SDCPatientMonitorConfigurationUpdatedPayload]
):
    __model__ = SDCPatientMonitorConfigurationUpdatedPayload
    __fake__ = Faker()


class SDCPatientMonitorConfigurationUpdatedEventFactory(
    ModelFactory[SDCPatientMonitorConfigurationUpdatedEvent]
):
    __model__ = SDCPatientMonitorConfigurationUpdatedEvent
    __fake__ = Faker()

    payload = SDCPatientMonitorConfigurationUpdatedPayloadFactory


class SDCPatientSessionStartedPayloadFactory(ModelFactory[SDCPatientSessionStartedPayload]):
    __model__ = SDCPatientSessionStartedPayload
    __fake__ = Faker()

    patient = SDCPatientPayloadFactory


class SDCPatientSessionStartedEventFactory(ModelFactory[SDCPatientSessionStartedEvent]):
    __model__ = SDCPatientSessionStartedEvent
    __fake__ = Faker()

    payload = SDCPatientSessionStartedPayloadFactory


class SDCPatientAdmissionRejectedPayloadFactory(ModelFactory[SDCPatientAdmissionRejectedPayload]):
    __model__ = SDCPatientAdmissionRejectedPayload
    __fake__ = Faker()

    patient = SDCPatientPayloadFactory


class SDCPatientAdmissionRejectedEventFactory(ModelFactory[SDCPatientAdmissionEvent]):
    __model__ = SDCPatientAdmissionEvent
    __fake__ = Faker()

    payload = SDCPatientSessionStartedPayloadFactory
