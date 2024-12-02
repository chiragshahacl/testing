# pylint: disable=R0801
import uuid
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.event_sourcing.stream import UpdateData
from app.device.src.common.event_sourcing.events import (
    CreateDeviceAlertEvent,
    CreateDeviceEvent,
    DeleteDeviceAlertEvent,
    DeleteDeviceEvent,
    DeviceAlertsUpdatedEvent,
    UpdateDeviceAlertEvent,
    UpdateDeviceInfoEvent,
)
from app.device.src.common.event_sourcing.stream import (
    AlertStream,
    DeviceEventStream,
)
from app.device.src.common.models import Device, DeviceAlert
from app.device.src.device.repository import (
    DeviceAlertRepository,
    ReadDeviceRepository,
    VitalsRangeRepository,
)
from app.device.src.device.schemas import (
    CreateDeviceAlertSchema,
    CreateDeviceSchema,
    UpdateDeviceAlertSchema,
    UpdateDeviceSchema,
)
from app.event_processing.topics.alerts.processors import process_alert_found_audit_log
from app.event_processing.topics.events_sdc.schemas import (
    SDCAlertPayload,
    SDCDevicePayload,
    SDCSensorPayload,
)
from app.settings import config


async def create_or_update_discovered_device(
    db_session: AsyncSession,
    device: Device,
    device_payload: SDCDevicePayload,
    gateway_id: uuid.UUID,
    patient_primary_identifier: Optional[str],
):
    event_stream = DeviceEventStream(db_session)
    device_repository = ReadDeviceRepository(db_session)

    device, device_created = await upsert_device(
        event_stream, device, device_payload, gateway_id, patient_primary_identifier
    )

    if device_created and not gateway_id:
        vitals_repository = VitalsRangeRepository(db_session)
        await vitals_repository.add_default_vital_ranges(device.id)

    if device_payload.connected_sensors is not None:
        await update_device_connected_sensors(
            event_stream,
            device_repository,
            device,
            patient_primary_identifier,
            device_payload.connected_sensors,
        )

    # Batch update all active alerts
    new_sensors = await device_repository.get_gateway_sensors(device.id)
    devices_by_identifier = {sensor.primary_identifier: sensor for sensor in new_sensors}
    # The device map must include the gateway
    devices_by_identifier[device.primary_identifier] = device
    await process_alerts(db_session, device.id, devices_by_identifier, device_payload.alerts)

    # Process all alert logs
    for alert_payload in device_payload.alerts:
        await process_alert_found_audit_log(db_session, alert_payload)


async def update_device_connected_sensors(
    event_stream: DeviceEventStream,
    repository: ReadDeviceRepository,
    gateway: Device,
    patient_primary_identifier: Optional[str],
    sensor_payload_list: List[SDCSensorPayload],
):
    sensor_payload_by_identifier = {
        sensor_payload.primary_identifier: sensor_payload for sensor_payload in sensor_payload_list
    }

    current_gateway_sensors = await repository.get_gateway_sensors(gateway_id=gateway.id)
    sensors_to_delete = [
        sensor
        for sensor in current_gateway_sensors
        if not sensor_payload_by_identifier.get(sensor.primary_identifier)
    ]
    await delete_sensors(event_stream, patient_primary_identifier, sensors_to_delete)

    existing_sensors = await repository.get_all_devices_by_primary_identifiers(
        primary_identifiers=sensor_payload_by_identifier.keys(),
    )
    sensors_to_update = [
        (sensor_payload_by_identifier.get(sensor.primary_identifier), sensor)
        for sensor in existing_sensors
    ]
    await update_sensors(event_stream, gateway, patient_primary_identifier, sensors_to_update)

    existing_sensors_primary_identifiers = [
        sensor.primary_identifier for sensor in existing_sensors
    ]
    sensors_to_create = [
        sensor_payload
        for sensor_payload in sensor_payload_by_identifier.values()
        if sensor_payload.primary_identifier not in existing_sensors_primary_identifiers
    ]
    await create_sensors(event_stream, gateway, patient_primary_identifier, sensors_to_create)


async def upsert_device(
    event_stream: DeviceEventStream,
    device: Device,
    device_payload: SDCDevicePayload,
    gateway_id: uuid.UUID,
    patient_primary_identifier: Optional[str],
) -> Tuple[Device, bool]:
    if device:
        logger.info("Device found, updating")
        payload = UpdateDeviceSchema(
            id=device.id,
            primary_identifier=device_payload.primary_identifier,
            name=device_payload.name,
            gateway_id=gateway_id,
            subject_identifier=patient_primary_identifier,
            model_number=device_payload.device_code,
            audio_pause_enabled=device_payload.config.audio_pause_enabled,
            audio_enabled=device_payload.config.audio_enabled,
        )
        event = UpdateDeviceInfoEvent(config.SYSTEM_USERNAME, payload)
    else:
        logger.info("Device not found, creating")
        payload = CreateDeviceSchema(
            id=uuid.uuid4(),
            primary_identifier=device_payload.primary_identifier,
            name=device_payload.name,
            gateway_id=gateway_id,
            subject_identifier=patient_primary_identifier,
            model_number=device_payload.device_code,
            audio_pause_enabled=device_payload.config.audio_pause_enabled,
            audio_enabled=device_payload.config.audio_enabled,
        )
        event = CreateDeviceEvent(config.SYSTEM_USERNAME, payload)
    return await event_stream.add(event, device), not device


async def create_sensors(
    event_stream: DeviceEventStream,
    device: Device,
    patient_primary_identifier: Optional[str],
    sensor_payloads: Iterable[SDCSensorPayload],
):
    def create_sensor_event_from_sensor_payload(payload: SDCSensorPayload) -> UpdateData[Device]:
        payload = CreateDeviceSchema(
            id=uuid.uuid4(),
            primary_identifier=payload.primary_identifier,
            name=payload.name,
            gateway_id=device.id,
            subject_identifier=patient_primary_identifier,
            model_number=payload.device_code,
            audio_pause_enabled=False,
            audio_enabled=True,
        )
        return CreateDeviceEvent(config.SYSTEM_USERNAME, payload), None

    sensor_events = [
        create_sensor_event_from_sensor_payload(payload) for payload in sensor_payloads
    ]
    await event_stream.batch_add(sensor_events)


async def update_sensors(
    event_stream: DeviceEventStream,
    device: Device,
    patient_primary_identifier: Optional[str],
    update_sensors_data: Iterable[Tuple[SDCSensorPayload, Device]],
):
    def update_sensor_event_from_update_data(
        update_sensor_pair: Tuple[SDCSensorPayload, Device],
    ) -> UpdateData[Device]:
        sensor_payload, sensor = update_sensor_pair
        payload = UpdateDeviceSchema(
            id=sensor.id,
            primary_identifier=sensor.primary_identifier,
            name=sensor_payload.name,
            gateway_id=device.id,
            subject_identifier=patient_primary_identifier,
            model_number=sensor_payload.device_code,
            audio_pause_enabled=False,
            audio_enabled=True,
        )
        return UpdateDeviceInfoEvent(config.SYSTEM_USERNAME, payload), sensor

    sensor_events = [
        update_sensor_event_from_update_data(update_sensor_pair)
        for update_sensor_pair in update_sensors_data
    ]
    await event_stream.batch_add(sensor_events)


async def delete_sensors(
    event_stream: DeviceEventStream,
    patient_primary_identifier: Optional[str],
    sensors: Iterable[Device],
):
    sensor_events = [(DeleteDeviceEvent(config.SYSTEM_USERNAME), sensor) for sensor in sensors]
    await event_stream.batch_delete(sensor_events, related_entity_id=patient_primary_identifier)


async def process_alert_payload(db_session: AsyncSession, alert_payload: SDCAlertPayload) -> None:
    alert_stream = AlertStream(db_session)
    stmt = (
        select(DeviceAlert)
        .join(Device)
        .where(DeviceAlert.code == alert_payload.code)
        .where(Device.primary_identifier == alert_payload.device_primary_identifier)
    )
    result = await db_session.execute(stmt)
    alert = result.scalars().first()
    if alert_payload.active:
        if not alert:
            logger.info("Creating Device Alert")
            stmt = select(Device).where(
                Device.primary_identifier == alert_payload.device_primary_identifier
            )
            result = await db_session.execute(stmt)
            device = result.scalars().first()
            payload = CreateDeviceAlertSchema.model_construct(
                device_id=device.id,
                code=alert_payload.code,
                priority=alert_payload.priority,
            )
            alert_event = CreateDeviceAlertEvent(config.SYSTEM_USERNAME, payload)
            await alert_stream.add(alert_event, None)
        else:
            logger.info("Updating Device Alert")
            payload = UpdateDeviceAlertSchema.model_construct(
                device_id=alert.device_id,
                code=alert_payload.code,
                priority=alert_payload.priority,
            )
            alert_event = UpdateDeviceAlertEvent(config.SYSTEM_USERNAME, payload)
            await alert_stream.add(alert_event, alert)
    elif alert and not alert_payload.active:
        logger.info("Deleting Device Alerts")
        delete_event = DeleteDeviceAlertEvent(config.SYSTEM_USERNAME)
        await alert_stream.delete(delete_event, alert)
    else:
        logger.info("No alert found")


async def process_alerts(
    db_session: AsyncSession,
    device_id: uuid.UUID,
    devices_by_identifier: Dict[str, Device],
    alert_payloads: Sequence[SDCAlertPayload],
) -> None:
    alert_stream = AlertStream(db_session)
    device_alert_repository = DeviceAlertRepository(db_session)

    def create_device_alert_from_alert_payload(payload: SDCAlertPayload) -> DeviceAlert:
        try:
            return DeviceAlert(
                id=uuid.uuid4(),
                code=payload.code,
                device_id=devices_by_identifier[payload.device_primary_identifier].id,
                priority=payload.priority,
            )
        except KeyError as e:
            logger.error(f"Found an alert {payload} with non-existing device.", e)
            raise e

    alerts_to_create = [
        create_device_alert_from_alert_payload(payload)
        for payload in alert_payloads
        if payload.active
    ]
    if alerts_to_create:
        await device_alert_repository.bulk_add(alerts_to_create)

    alerts_to_delete = [
        create_device_alert_from_alert_payload(payload)
        for payload in alert_payloads
        if not payload.active
    ]
    if alerts_to_delete:
        await device_alert_repository.bulk_delete(alerts_to_delete)

    await alert_stream.notify(DeviceAlertsUpdatedEvent(config.SYSTEM_USERNAME), device_id)
