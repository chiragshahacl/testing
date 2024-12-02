import decimal
import enum
import uuid
from datetime import datetime

import numpy as np
import orjson
from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context

from src.common.schemas import (
    ConfigSchema,
    ConnectedSensorSchema,
    DeviceConnectedPayloadSchema,
    DeviceConnectedSchema,
    DeviceSchema,
    PatientAdmissionRejectedPayload,
    PatientAdmissionRejectedSchema,
    PatientEncryptedSchema,
    PatientSessionClosedPayloadSchema,
    PatientSessionClosedSchema,
    SensorRemovedPayloadSchema,
    SensorRemovedSchema,
    UpdatePatientMonitorConfigPayload,
    UpdatePatientMonitorConfigSchema,
)
from src.settings import settings


class KafkaClientFactory:
    def __init__(self):
        self.client = None

    async def __call__(self, *args, **kwargs):
        if not self.client:
            url = f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}"
            if settings.ENVIRONMENT == "local":
                self.client = AIOKafkaProducer(bootstrap_servers=url)
            else:
                ssl_context = create_ssl_context(
                    cafile=settings.KAFKA_CA_FILE_PATH,
                    certfile=settings.KAFKA_CERT_FILE_PATH,
                    keyfile=settings.KAFKA_KEY_FILE_PATH,
                    password=settings.KAFKA_PASSWORD,
                )
                self.client = AIOKafkaProducer(
                    bootstrap_servers=f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
                    security_protocol="SSL",
                    ssl_context=ssl_context,
                )
            await self.client.start()
        return self.client


KafkaClient = KafkaClientFactory()


def orjson_default_encode(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, np.float64):
        return float(decimal.Decimal(str(obj)))
    if isinstance(obj, enum.Enum):
        return obj.value
    raise TypeError


# pylint: disable=E1101
async def publish(data: dict, patient_primary_identifier: str) -> None:
    client = await KafkaClient()

    await client.send_and_wait(
        topic=settings.KAFKA_VITALS_TOPIC,
        value=orjson.dumps(data, default=orjson_default_encode),
        key=str.encode(patient_primary_identifier),
        headers=[
            ("event_type", str.encode(data["event_type"])),
            ("code", str.encode(data["payload"]["code"])),
            (
                "device_primary_identifier",
                str.encode(data["payload"]["device_primary_identifier"]),
            ),
        ],
    )


async def publish_alert(
    data: dict, patient_primary_identifier: str, is_technical_alert: bool
) -> None:
    client = await KafkaClient()
    alert_topic = settings.KAFKA_ALERTS_TOPIC
    headers = [("event_type", str.encode(data["event_type"]))]

    if is_technical_alert:
        alert_topic = settings.KAFKA_TECHNICAL_ALERTS_TOPIC
        headers.append(("patient_primary_identifier", str.encode(patient_primary_identifier)))

    await client.send_and_wait(
        topic=alert_topic,
        value=orjson.dumps(data, default=orjson_default_encode),
        key=str.encode(patient_primary_identifier),
        headers=headers,
    )


async def publish_device_ranges(payload, device_primary_identifier: str) -> None:
    range_data = {
        "message_id": str(uuid.uuid4()),
        "event_type": "DEVICE_NEW_VITALS_RANGES",
        "event_name": "Device new vitals ranges added",
        "timestamp": str(int(datetime.now().timestamp() * 1000)),
        "payload": payload.dict(),
    }
    client = await KafkaClient()
    await client.send(
        topic=settings.KAFKA_DEVICE_TOPIC,
        value=orjson.dumps(range_data, default=orjson_default_encode),
        key=str.encode(device_primary_identifier),
        headers=[("event_type", str.encode(range_data["event_type"]))],
    )


async def publish_pm_connection_status(device_primary_identifier: str, status=True) -> None:
    connection_status_data = {
        "message_id": str(uuid.uuid4()),
        "event_type": "PM_CONNECTION_STATUS_REPORT",
        "event_name": "PM connection status",
        "timestamp": str(int(datetime.now().timestamp() * 1000)),
        "payload": {
            "connection_status": status,
            "device_primary_identifier": device_primary_identifier,
        },
    }
    client = await KafkaClient()
    await client.send(
        topic=settings.KAFKA_SDC_REALTIME_STATE_TOPIC,
        value=orjson.dumps(connection_status_data, default=orjson_default_encode),
        key=str.encode(device_primary_identifier),
        headers=[("event_type", str.encode(connection_status_data["event_type"]))],
    )


async def publish_device_discovered(device) -> None:
    connected_sensor_message = None

    if hasattr(device, "sensors") and device.sensors:
        connected_sensor_message = [
            ConnectedSensorSchema(
                primary_identifier=sensor.primary_identifier,
                name=sensor.name,
                device_code=sensor.device_code,
            )
            for sensor in device.sensors
        ]

    config_message = None
    if hasattr(device, "config") and device.config:
        config_message = ConfigSchema(
            audio_pause_enabled=device.config.audio_pause_enabled,
            audio_enabled=device.config.audio_enabled,
        )
    else:
        config_message = ConfigSchema()

    device_message = DeviceSchema(
        primary_identifier=device.primary_identifier,
        name=device.name,
        device_code=device.device_code,
        connected_sensors=connected_sensor_message if connected_sensor_message else None,
        config=config_message,
        gateway_id=device.patient_monitor.primary_identifier
        if hasattr(device, "patient_monitor")
        else None,
    )
    patient_message = None

    if device.patient:
        patient_message = PatientEncryptedSchema(
            primary_identifier=device.patient.primary_identifier,
            given_name=device.patient.given_name,
            family_name=device.patient.family_name,
            gender=device.patient.gender,
            birth_date=device.patient.birth_date,
        )

    message_payload = DeviceConnectedPayloadSchema(
        device=device_message,
        patient=patient_message,
    )

    message_wrapper = DeviceConnectedSchema(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.now().strftime(settings.TIMESTAMP_FORMAT),
        payload=message_payload,
    )

    client = await KafkaClient()
    await client.send_and_wait(
        topic=settings.KAFKA_DEVICE_TOPIC,
        value=orjson.dumps(message_wrapper.dict(), default=orjson_default_encode),
        key=str.encode(device.primary_identifier),
        headers=[("event_type", str.encode(message_wrapper.event_type))],
    )


async def publish_sensor_removed(
    sensor_primary_identifier: str, device_type: str, patient_primary_identifier: str
) -> None:
    message_payload = SensorRemovedPayloadSchema(
        device_primary_identifier=sensor_primary_identifier,
        device_type=device_type,
        patient_primary_identifier=patient_primary_identifier,
        determination_time=datetime.now().strftime(settings.TIMESTAMP_FORMAT),
    )
    message_wrapper = SensorRemovedSchema(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.now().strftime(settings.TIMESTAMP_FORMAT),
        payload=message_payload,
    )

    client = await KafkaClient()
    await client.send_and_wait(
        topic=settings.KAFKA_DEVICE_TOPIC,
        value=orjson.dumps(message_wrapper.dict(), default=orjson_default_encode),
        key=str.encode(sensor_primary_identifier),
        headers=[("event_type", str.encode(message_wrapper.event_type))],
    )


async def publish_patient_session_closed(
    monitor_primary_identifier: str, patient_primary_identifier: str
) -> None:
    message_payload = PatientSessionClosedPayloadSchema(
        device_primary_identifier=monitor_primary_identifier,
        patient_primary_identifier=patient_primary_identifier,
    )
    message_wrapper = PatientSessionClosedSchema(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.now().strftime(settings.TIMESTAMP_FORMAT),
        payload=message_payload,
    )

    client = await KafkaClient()
    await client.send_and_wait(
        topic=settings.KAFKA_DEVICE_TOPIC,
        value=orjson.dumps(message_wrapper.dict(), default=orjson_default_encode),
        key=str.encode(patient_primary_identifier),
        headers=[("event_type", str.encode(message_wrapper.event_type))],
    )


async def publish_update_patient_monitor_configuration(
    device,
) -> None:
    message_payload = UpdatePatientMonitorConfigPayload(
        device_primary_identifier=device.primary_identifier,
        audio_enabled=device.config.audio_enabled,
        audio_pause_enabled=device.config.audio_pause_enabled,
    )

    message_wrapper = UpdatePatientMonitorConfigSchema(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.now().strftime(settings.TIMESTAMP_FORMAT),
        payload=message_payload,
    )

    client = await KafkaClient()
    await client.send_and_wait(
        topic=settings.KAFKA_DEVICE_TOPIC,
        value=orjson.dumps(message_wrapper.dict(), default=orjson_default_encode),
        key=str.encode(device.device_primary_identifier),
        headers=[("event_type", str.encode(message_wrapper.event_type))],
    )


async def publish_reject_patient_admission(
    monitor_primary_identifier: str,
    patient_primary_identifier: str,
) -> None:
    message_payload = PatientAdmissionRejectedPayload(
        device_primary_identifier=monitor_primary_identifier,
        patient_primary_identifier=patient_primary_identifier,
    )
    message_wrapper = PatientAdmissionRejectedSchema(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.now().strftime(settings.TIMESTAMP_FORMAT),
        payload=message_payload,
    )
    client = await KafkaClient()
    await client.send_and_wait(
        topic=settings.KAFKA_DEVICE_TOPIC,
        value=orjson.dumps(message_wrapper.dict(), default=orjson_default_encode),
        key=str.encode(monitor_primary_identifier),
        headers=[("event_type", str.encode(message_wrapper.event_type))],
    )
