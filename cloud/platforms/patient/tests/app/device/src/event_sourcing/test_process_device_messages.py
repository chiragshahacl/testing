from uuid import uuid4

import pytest
from features.factories.broker import BrokerMessageFactory
from features.factories.device_factories import (
    DeviceAlertFactory,
    DeviceFactory,
    DeviceVitalRangeFactory,
)
from features.factories.sdc import (
    SDCAlertPayloadFactory,
    SDCDeviceDiscoveredEventFactory,
    SDCDeviceDiscoveredPayloadFactory,
    SDCDevicePayloadFactory,
    SDCNewAlertEventFactory,
    SDCNewVitalsRangesEventFactory,
    SDCNewVitalsRangesPayloadFactory,
    SDCPatientMonitorConfigurationUpdatedEventFactory,
    SDCPatientMonitorConfigurationUpdatedPayloadFactory,
    SDCPatientPayloadFactory,
    SDCPatientSessionClosedEventFactory,
    SDCPatientSessionClosedPayloadFactory,
    SDCSensorPayloadFactory,
    SDCSensorRemovedEventFactory,
    SDCSensorRemovedPayloadFactory,
)
from sqlalchemy import select

from app.device.src.common.models import Device, DeviceAlert, DeviceVitalRange
from app.device.src.device.repository import DEVICE_DEFAULT_VITALS
from app.event_processing.topics.events_sdc.processors import (
    process_device_discovered_event_for_device,
    process_device_vital_range_message,
    process_patient_session_ended_event_for_device,
    process_sensor_removed_event_for_device,
    process_technical_alerts,
    process_updated_pm_config,
)
from app.event_processing.topics.events_sdc.schemas import (
    SDCNewVitalsRangesEvent,
)
from app.settings import config


@pytest.mark.asyncio
async def test_new_device_vital_range_discovered_backfill(async_db_session):
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()
    existing = []
    for i in range(5):
        evr = DeviceVitalRangeFactory.build(device_id=device.id, code=f"code-{i}")
        existing.append(evr)
        async_db_session.add(evr)

        await async_db_session.flush()

    payload = SDCNewVitalsRangesPayloadFactory.build(primary_identifier=device.primary_identifier)
    event: SDCNewVitalsRangesEvent = SDCNewVitalsRangesEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(
        source_topic=config.EVENTS_SDC_TOPIC, value=event.model_dump_json()
    )

    await process_device_vital_range_message(async_db_session, broker_message)

    stmt = (
        select(DeviceVitalRange)
        .join(Device)
        .where(Device.id == DeviceVitalRange.device_id)
        .where(Device.primary_identifier == device.primary_identifier)
        .where(DeviceVitalRange.code.in_([v.code for v in event.payload.ranges]))
    )
    result = await async_db_session.execute(stmt)
    device_vrs = result.scalars().all()
    dvr_map = {item.code: (item.lower_limit, item.upper_limit) for item in event.payload.ranges}
    device_map = {item.code: (item.lower_limit, item.upper_limit) for item in device_vrs}
    for code in device_map:
        assert code != "bad-code"
        assert dvr_map[code] == device_map[code]


@pytest.mark.asyncio
async def test_update_existing_device_alert_discovered(async_db_session):
    device = DeviceFactory.build()

    payload = SDCAlertPayloadFactory.build(device_primary_identifier=device.primary_identifier)
    message = SDCNewAlertEventFactory.build(payload=payload)
    alert = DeviceAlertFactory.build(device_id=device.id, code=payload.code)
    async_db_session.add(device)
    async_db_session.add(alert)
    await async_db_session.flush()

    broker_message = BrokerMessageFactory.build(
        source_topic=config.EVENTS_SDC_TOPIC, value=message.model_dump_json()
    )

    await process_technical_alerts(async_db_session, broker_message)

    stmt = (
        select(DeviceAlert)
        .join(Device)
        .where(Device.primary_identifier == device.primary_identifier)
        .where(DeviceAlert.code == alert.code)
    )
    result = await async_db_session.execute(stmt)
    alert = result.scalars().one()

    assert alert
    assert alert.code == payload.code


@pytest.mark.asyncio
async def test_delete_existing_device_alert_discovered(async_db_session):
    device = DeviceFactory.build()
    alert = DeviceAlertFactory.build()
    alert.device_id = device.id
    alert.code = "14502542"
    async_db_session.add(device)
    async_db_session.add(alert)
    await async_db_session.flush()

    payload = SDCAlertPayloadFactory.build(
        device_primary_identifier=device.primary_identifier,
        code=alert.code,
        active=False,
    )
    message = SDCNewAlertEventFactory.build(payload=payload)

    broker_message = BrokerMessageFactory.build(
        source_topic=config.EVENTS_SDC_TOPIC, value=message.model_dump_json()
    )

    await process_technical_alerts(async_db_session, broker_message)

    stmt = (
        select(DeviceAlert)
        .join(Device)
        .where(Device.primary_identifier == payload.device_primary_identifier)
        .where(DeviceAlert.code == payload.code)
    )
    result = await async_db_session.execute(stmt)
    alert = result.scalars().first()

    assert not alert


@pytest.mark.asyncio
async def test_process_technical_alert_alert_not_found(async_db_session):
    device = DeviceFactory.build()
    alert = DeviceAlertFactory.build()
    alert.device_id = device.id
    alert.code = "14502542"
    async_db_session.add(device)
    await async_db_session.flush()

    payload = SDCAlertPayloadFactory.build(
        device_primary_identifier=device.primary_identifier,
        code=alert.code,
        active=False,
    )
    message = SDCNewAlertEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(
        source_topic=config.EVENTS_SDC_TOPIC, value=message.model_dump_json()
    )

    await process_technical_alerts(async_db_session, broker_message)

    stmt = (
        select(DeviceAlert)
        .join(Device)
        .where(Device.primary_identifier == payload.device_primary_identifier)
        .where(DeviceAlert.code == payload.code)
    )
    result = await async_db_session.execute(stmt)
    alert = result.scalars().first()

    assert not alert


@pytest.mark.asyncio
async def test_new_device_discovered(async_db_session):
    payload = SDCDeviceDiscoveredPayloadFactory().build(patient=None)
    event = SDCDeviceDiscoveredEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_device_discovered_event_for_device(async_db_session, broker_message)

    stmt = select(Device).where(
        Device.primary_identifier == event.payload.device.primary_identifier
    )
    result = await async_db_session.execute(stmt)
    device = result.scalars().one()

    assert device
    assert device.name == event.payload.device.name
    assert device.gateway_id == event.payload.device.gateway_id
    assert device.audio_enabled == event.payload.device.config.audio_enabled
    assert device.audio_pause_enabled == event.payload.device.config.audio_pause_enabled


@pytest.mark.asyncio
async def test_new_pm_discovered_with_new_sensor(async_db_session):
    sensor_payload = SDCSensorPayloadFactory.build(
        primary_identifier="SEM-0001",
        name="ANNE Chest",
        device_code="ANNE Chest",
    )
    device_payload = SDCDevicePayloadFactory.build(connected_sensors=[sensor_payload])
    payload = SDCDeviceDiscoveredPayloadFactory.build(device=device_payload)
    event = SDCDeviceDiscoveredEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_device_discovered_event_for_device(async_db_session, broker_message)

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == device_payload.primary_identifier)
    )
    pm = result.scalars().one()

    assert pm.name == device_payload.name
    assert pm.gateway_id == device_payload.gateway_id

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == sensor_payload.primary_identifier)
    )
    actual_sensor = result.scalars().one()

    assert actual_sensor.name == sensor_payload.name
    assert actual_sensor.gateway_id == pm.id


@pytest.mark.asyncio
async def test_new_pm_discovered_with_new_sensor_and_alarm(async_db_session):
    sensor_primary_identifier = "SEM-0001"
    sensor_payload = SDCSensorPayloadFactory.build(
        primary_identifier=sensor_primary_identifier,
        name="ANNE Chest",
        device_code="ANNE Chest",
    )
    alert_payload = SDCAlertPayloadFactory.build(
        device_primary_identifier=sensor_primary_identifier
    )
    device_payload = SDCDevicePayloadFactory.build(
        connected_sensors=[sensor_payload], alerts=[alert_payload]
    )
    payload = SDCDeviceDiscoveredPayloadFactory.build(device=device_payload)
    event = SDCDeviceDiscoveredEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_device_discovered_event_for_device(async_db_session, broker_message)

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == device_payload.primary_identifier)
    )
    pm = result.scalars().one()

    assert pm
    assert pm.name == device_payload.name
    assert pm.gateway_id is None

    # Verify sensor created
    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == sensor_payload.primary_identifier)
    )
    actual_sensor = result.scalars().one()

    assert actual_sensor
    assert actual_sensor.name == sensor_payload.name
    assert actual_sensor.gateway_id == pm.id

    # Verify alert added
    stmt = (
        select(DeviceAlert)
        .join(Device)
        .where(Device.primary_identifier == alert_payload.device_primary_identifier)
        .where(DeviceAlert.code == alert_payload.code)
    )
    result = await async_db_session.execute(stmt)
    alert = result.scalars().one()

    assert alert
    assert alert.code == alert_payload.code


@pytest.mark.asyncio
async def test_new_device_discovered_no_patient(async_db_session):
    device_payload = SDCDevicePayloadFactory.build(connected_sensors=[], alerts=[])
    payload = SDCDeviceDiscoveredPayloadFactory.build(device=device_payload, patient=None)
    event = SDCDeviceDiscoveredEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_device_discovered_event_for_device(async_db_session, broker_message)

    stmt = select(Device).where(Device.primary_identifier == device_payload.primary_identifier)
    result = await async_db_session.execute(stmt)
    device = result.scalars().one()

    assert device
    assert device.name == device_payload.name
    assert device.gateway_id is None
    assert device.subject_identifier is None


@pytest.mark.asyncio
async def test_new_device_vital_range_discovered(async_db_session):
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()

    payload = SDCNewVitalsRangesPayloadFactory.build(primary_identifier=device.primary_identifier)
    event = SDCNewVitalsRangesEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_device_vital_range_message(async_db_session, broker_message)

    stmt = (
        select(DeviceVitalRange)
        .join(Device)
        .where(Device.id == DeviceVitalRange.device_id)
        .where(Device.primary_identifier == device.primary_identifier)
    )
    result = await async_db_session.execute(stmt)
    device_vrs = result.scalars().all()
    dvr_map = {item.code: (item.lower_limit, item.upper_limit) for item in payload.ranges}
    real_device_map = {item.code: (item.lower_limit, item.upper_limit) for item in device_vrs}
    for code in dvr_map:
        assert code != "bad-code"
        assert dvr_map[code] == real_device_map[code]


@pytest.mark.asyncio
async def test_vital_range_discovered_existing_ranges(async_db_session):
    device = DeviceFactory.build()
    async_db_session.add(device)
    await async_db_session.flush()
    existing = []

    for i in range(5):
        evr = DeviceVitalRangeFactory.build(device_id=device.id, code=f"code-{i}")
        existing.append(evr)
        async_db_session.add(evr)
        await async_db_session.flush()

    payload = SDCNewVitalsRangesPayloadFactory.build(primary_identifier=device.primary_identifier)
    event = SDCNewVitalsRangesEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_device_vital_range_message(async_db_session, broker_message)

    stmt = (
        select(DeviceVitalRange)
        .join(Device)
        .where(Device.id == DeviceVitalRange.device_id)
        .where(Device.primary_identifier == device.primary_identifier)
        .where(DeviceVitalRange.code.in_([v.code for v in payload.ranges]))
    )
    result = await async_db_session.execute(stmt)
    device_vrs = result.scalars().all()
    dvr_map = {item.code: (item.lower_limit, item.upper_limit) for item in payload.ranges}
    device_map = {item.code: (item.lower_limit, item.upper_limit) for item in device_vrs}
    for code in device_map:
        assert code != "bad-code"
        assert dvr_map[code] == device_map[code]


@pytest.mark.asyncio
async def test_already_discovered_device_discovered_again_significant_changes(
    async_db_session,
):
    pm = DeviceFactory.build(subject_identifier="123", gateway_id=None)
    new_pm = DeviceFactory.build(subject_identifier="123")
    sensor = DeviceFactory.build(subject_identifier="123")
    sensor.gateway_id = pm.id
    async_db_session.add_all([pm, new_pm, sensor])
    await async_db_session.flush()

    device_payload = SDCDevicePayloadFactory.build(
        primary_identifier=sensor.primary_identifier,
        name=sensor.name,
        gateway_id=None,
        device_code=sensor.model_number,
    )
    patient_payload = SDCPatientPayloadFactory.build(primary_identifier=sensor.subject_identifier)
    payload = SDCDeviceDiscoveredPayloadFactory.build(
        device=device_payload, patient=patient_payload
    )
    event = SDCDeviceDiscoveredEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(
        value=event.model_dump_json(), source_topic=config.EVENTS_SDC_TOPIC
    )

    await process_device_discovered_event_for_device(async_db_session, broker_message)

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == device_payload.primary_identifier)
    )
    modified_device = result.scalars().one()

    assert modified_device
    assert modified_device.gateway_id == new_pm.gateway_id


@pytest.mark.asyncio
async def test_already_discovered_pm_discovered_with_new_sensor(async_db_session):
    pm = DeviceFactory.build(subject_identifier="123")
    old_sensor = DeviceFactory.build()
    old_sensor.gateway_id = pm.id
    old_sensor.subject_identifier = pm.subject_identifier
    async_db_session.add_all([pm, old_sensor])
    await async_db_session.flush()

    new_sensor_payload = SDCSensorPayloadFactory.build(
        primary_identifier="SEM-0001",
        name="ANNE Chest",
        gateway_id=pm.primary_identifier,
        device_code="ANNE Chest",
    )
    device_payload = SDCDevicePayloadFactory.build(
        primary_identifier=pm.primary_identifier,
        name=pm.name,
        gateway_id=None,
        device_code=pm.model_number,
        connected_sensors=[new_sensor_payload],
    )
    patient_payload = SDCPatientPayloadFactory.build(primary_identifier=pm.subject_identifier)
    payload = SDCDeviceDiscoveredPayloadFactory.build(
        device=device_payload, patient=patient_payload
    )
    event = SDCDeviceDiscoveredEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_device_discovered_event_for_device(async_db_session, broker_message)

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == pm.primary_identifier)
    )
    actual_pm = result.scalars().one()

    assert actual_pm
    assert actual_pm.name == pm.name
    assert actual_pm.gateway_id == pm.gateway_id

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == old_sensor.primary_identifier)
    )
    actual_old_sensor = result.scalars().one_or_none()

    assert not actual_old_sensor

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == new_sensor_payload.primary_identifier)
    )
    actual_new_sensor = result.scalars().one()

    assert actual_new_sensor
    assert actual_new_sensor.name == new_sensor_payload.name
    assert actual_new_sensor.gateway_id == pm.id


@pytest.mark.asyncio
async def test_already_discovered_pm_discovered_with_another_existing_sensor(
    async_db_session,
):
    pm = DeviceFactory.build()
    old_sensor = DeviceFactory.build()
    old_sensor.gateway_id = pm.id
    old_sensor.subject_identifier = pm.subject_identifier
    other_pm = DeviceFactory.build()
    new_sensor = DeviceFactory.build()
    new_sensor.gateway_id = other_pm.id
    new_sensor.subject_identifier = other_pm.subject_identifier
    async_db_session.add_all([pm, other_pm, old_sensor, new_sensor])
    await async_db_session.flush()

    new_sensor_payload = SDCSensorPayloadFactory.build(
        primary_identifier=new_sensor.primary_identifier,
        name=new_sensor.name,
        gateway_id=pm.primary_identifier,
        device_code="ANNE Chest",
    )
    device_payload = SDCDevicePayloadFactory.build(
        primary_identifier=pm.primary_identifier,
        name=pm.name,
        gateway_id=None,
        device_code=pm.model_number,
        connected_sensors=[new_sensor_payload],
    )
    patient_payload = SDCPatientPayloadFactory.build()
    payload = SDCDeviceDiscoveredPayloadFactory.build(
        device=device_payload, patient=patient_payload
    )
    event = SDCDeviceDiscoveredEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_device_discovered_event_for_device(async_db_session, broker_message)

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == pm.primary_identifier)
    )
    actual_pm = result.scalars().one()

    assert actual_pm
    assert actual_pm.name == pm.name
    assert actual_pm.gateway_id == pm.gateway_id

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == old_sensor.primary_identifier)
    )
    actual_old_sensor = result.scalars().one_or_none()

    assert not actual_old_sensor

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == new_sensor_payload.primary_identifier)
    )
    actual_new_sensor = result.scalars().one()

    assert actual_new_sensor
    assert actual_new_sensor.name == new_sensor_payload.name
    assert actual_new_sensor.gateway_id == pm.id
    assert actual_new_sensor.subject_identifier == patient_payload.primary_identifier


@pytest.mark.asyncio
async def test_already_discovered_pm_discovered_with_same_sensor(async_db_session):
    pm = DeviceFactory.build()
    sensor = DeviceFactory.build()
    sensor.gateway_id = pm.id
    sensor.subject_identifier = pm.subject_identifier
    async_db_session.add_all([pm, sensor])
    await async_db_session.flush()

    new_sensor_payload = SDCSensorPayloadFactory.build(
        primary_identifier=sensor.primary_identifier,
        name=sensor.name,
        gateway_id=pm.primary_identifier,
        device_code=sensor.name,
    )
    device_payload = SDCDevicePayloadFactory.build(
        primary_identifier=pm.primary_identifier,
        name=pm.name,
        gateway_id=None,
        device_code=pm.model_number,
        connected_sensors=[new_sensor_payload],
    )
    patient_payload = SDCPatientPayloadFactory.build()
    payload = SDCDeviceDiscoveredPayloadFactory.build(
        device=device_payload, patient=patient_payload
    )
    event = SDCDeviceDiscoveredEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_device_discovered_event_for_device(async_db_session, broker_message)

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == pm.primary_identifier)
    )
    actual_pm = result.scalars().one()

    assert actual_pm
    assert actual_pm.name == pm.name
    assert actual_pm.gateway_id == pm.gateway_id

    result = await async_db_session.execute(
        select(Device).where(Device.primary_identifier == sensor.primary_identifier)
    )
    actual_sensor = result.scalars().one()

    assert actual_sensor
    assert actual_sensor.name == sensor.name
    assert actual_sensor.gateway_id == pm.id


@pytest.mark.asyncio
async def test_new_device_discovered_with_default_vitals(async_db_session):
    device_payload = SDCDevicePayloadFactory.build(device_code="145100")
    payload = SDCDeviceDiscoveredPayloadFactory.build(device=device_payload)
    event = SDCDeviceDiscoveredEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_device_discovered_event_for_device(async_db_session, broker_message)

    stmt = select(Device).where(Device.primary_identifier == device_payload.primary_identifier)
    result = await async_db_session.execute(stmt)
    device = result.scalars().one()

    assert device
    assert device.name == device_payload.name
    assert device.gateway_id == device_payload.gateway_id

    # test that the new device has Vitals
    vital_stmt = select(DeviceVitalRange).where(device.id == DeviceVitalRange.device_id)
    vital_result = await async_db_session.execute(vital_stmt)
    vitals = vital_result.scalars().all()
    dvr_map = {vital.code: vital for vital in vitals}
    for dvr in DEVICE_DEFAULT_VITALS:
        assert dvr["code"] in dvr_map
        assert dvr_map[dvr["code"]].upper_limit == dvr["upper_limit"]
        assert dvr_map[dvr["code"]].lower_limit == dvr["lower_limit"]


@pytest.mark.asyncio
async def test_sensor_removed_event(async_db_session):
    pm = DeviceFactory.build()
    async_db_session.add(pm)
    await async_db_session.flush()

    sensor = DeviceFactory.build()
    sensor.gateway_id = pm.id
    async_db_session.add(sensor)
    await async_db_session.flush()

    payload = SDCSensorRemovedPayloadFactory.build(
        device_primary_identifier=sensor.primary_identifier
    )
    event = SDCSensorRemovedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_sensor_removed_event_for_device(async_db_session, broker_message)

    stmt = select(Device).where(Device.primary_identifier == sensor.primary_identifier)
    result = await async_db_session.execute(stmt)
    found_device = result.scalars().one_or_none()
    assert found_device is None


@pytest.mark.asyncio
async def test_sensor_removed_event_trying_to_remove_patient_monitor(async_db_session):
    pm = DeviceFactory.build()
    async_db_session.add(pm)
    await async_db_session.flush()

    payload = SDCSensorRemovedPayloadFactory.build(device_primary_identifier=pm.primary_identifier)
    event = SDCSensorRemovedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_sensor_removed_event_for_device(async_db_session, broker_message)

    stmt = select(Device).where(Device.primary_identifier == pm.primary_identifier)
    result = await async_db_session.execute(stmt)
    found_device = result.scalars().one_or_none()
    assert str(found_device.id) == str(pm.id)


@pytest.mark.asyncio
async def test_sensor_removed_event_trying_to_non_existing_sensor(async_db_session):
    pm = DeviceFactory.build()
    async_db_session.add(pm)
    await async_db_session.flush()

    sensor = DeviceFactory.build(gateway_id=pm.id)
    async_db_session.add(sensor)
    await async_db_session.flush()

    non_existing_identifier = "non-existing"
    payload = SDCSensorRemovedPayloadFactory.build(
        device_primary_identifier=non_existing_identifier
    )
    event = SDCSensorRemovedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_sensor_removed_event_for_device(async_db_session, broker_message)

    stmt = select(Device)
    result = await async_db_session.execute(stmt)
    found_devices = [dev.id for dev in result.scalars().all()]
    for device_id in [pm.id, sensor.id]:
        assert device_id in found_devices


@pytest.mark.asyncio
async def test_patient_session_closed_event(async_db_session):
    pm = DeviceFactory.build(subject_identifier="PATIENT-001")
    async_db_session.add(pm)
    await async_db_session.flush()

    sensor = DeviceFactory.build(gateway_id=pm.id, subject_identifier=pm.subject_identifier)
    async_db_session.add(sensor)
    await async_db_session.flush()

    sensor_2 = DeviceFactory.build(subject_identifier="PATIENT-002")
    async_db_session.add(sensor_2)
    await async_db_session.flush()

    payload = SDCPatientSessionClosedPayloadFactory.build(
        device_primary_identifier=pm.primary_identifier,
        patient_primary_identifier=pm.subject_identifier,
    )
    event = SDCPatientSessionClosedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_patient_session_ended_event_for_device(async_db_session, broker_message)

    await async_db_session.refresh(pm)
    await async_db_session.refresh(sensor)
    await async_db_session.refresh(sensor_2)


@pytest.mark.asyncio
async def test_patient_session_closed_event_no_devices_found(async_db_session):
    payload = SDCPatientSessionClosedPayloadFactory.build(
        device_primary_identifier=str(uuid4()),
        patient_primary_identifier=str(uuid4()),
    )
    event = SDCPatientSessionClosedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    ret_value = await process_patient_session_ended_event_for_device(
        async_db_session, broker_message
    )
    assert ret_value is None


@pytest.mark.asyncio
async def test_delete_alerts_on_patient_session_closed_event(async_db_session):
    pm = DeviceFactory.build(subject_identifier="PATIENT-001")
    async_db_session.add(pm)
    await async_db_session.flush()

    sensor = DeviceFactory.build(gateway_id=pm.id, subject_identifier=pm.subject_identifier)
    async_db_session.add(sensor)
    await async_db_session.flush()

    alert = DeviceAlertFactory.build(device_id=sensor.id, code="14502542")
    async_db_session.add(alert)
    await async_db_session.flush()

    payload = SDCPatientSessionClosedPayloadFactory.build(
        device_primary_identifier=pm.primary_identifier,
        patient_primary_identifier=pm.subject_identifier,
    )
    event = SDCPatientSessionClosedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_patient_session_ended_event_for_device(async_db_session, broker_message)

    await async_db_session.refresh(pm)
    await async_db_session.refresh(sensor)

    stmt = select(DeviceAlert)
    result = await async_db_session.execute(stmt)
    alerts = result.scalars().all()
    assert not alerts


@pytest.mark.asyncio
async def test_pm_config_updated(async_db_session):
    pm = DeviceFactory.build()
    async_db_session.add(pm)
    await async_db_session.flush()

    payload = SDCPatientMonitorConfigurationUpdatedPayloadFactory.build(
        device_primary_identifier=pm.primary_identifier
    )
    event = SDCPatientMonitorConfigurationUpdatedEventFactory.build(payload=payload)
    broker_message = BrokerMessageFactory.build(value=event.model_dump_json())

    await process_updated_pm_config(async_db_session, broker_message)

    device_primary_identifier = pm.primary_identifier
    stmt = select(Device).where(Device.primary_identifier == device_primary_identifier)
    result = await async_db_session.execute(stmt)
    device = result.scalars().one()

    assert device
    assert device.primary_identifier == device_primary_identifier
    assert device.audio_pause_enabled == payload.audio_pause_enabled
    assert device.audio_enabled == payload.audio_enabled
