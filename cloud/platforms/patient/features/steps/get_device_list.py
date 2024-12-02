from uuid import UUID, uuid4

import dateutil.parser
from behave import (
    step,
    when,
)

from app.device.src.common.models import Device
from features.steps.device_common import create_alarms_and_vitals


@step("a request to get a device list by multiple locations")
def step_impl(context):
    context.device1_id = "91e6c14f-1142-49c8-9898-971b726b9684"
    context.device1_primary_identifier = "primary-identifier"
    context.device1_name = "device1"
    context.device1_location = "1a3abaa6-e9c8-414b-9d01-f2c861c3c716"
    context.device2_id = "91e6c14f-1142-49c8-9898-971b726b9685"
    context.device2_primary_identifier = "primary-identifier-1"
    context.device2_name = "device2"
    context.device2_location = "1a3abaa6-e9c8-414b-9d01-f2c861c3c717"
    context.bed_ids = [context.device1_location, context.device2_location]
    context.request = {
        "url": f"/device?location_id={context.device1_location}&location_id={context.device2_location}",
    }


@step("a request to get a device list by device code only")
def step_impl(context):
    context.device_id = "91e6c14f-1142-49c8-9898-971b726b9684"
    context.device_primary_identifier = "primary-identifier"
    context.device_name = "device"
    context.device_code = "test-device"
    context.request = {
        "url": f"/device?device_code={context.device_code}",
    }


@step("a request to get a device list by gateway and location")
def step_impl(context):
    context.device_id = "91e6c14f-1142-49c8-9898-971b726b9684"
    context.device_primary_identifier = "primary-identifier"
    context.device_name = "device"
    context.gateway_id = uuid4()
    context.bed_id = str(uuid4())
    context.request = {
        "url": f"/device?gateway={context.gateway_id}&location_id={context.bed_id}",
    }


@step("a request to get a device list by gateway_id")
def step_impl(context):
    context.gateway_id = uuid4()
    context.bed_id = str(uuid4())
    context.request = {
        "url": f"/device?gateway={context.gateway_id}",
    }


@step("a request to get a device list by is_gateway")
def step_impl(context):
    context.request = {
        "url": f"/device?is_gateway={True}",
    }


@step("a request to get a device list by gateway and location and is_gateway")
def step_impl(context):
    context.gateway_id = uuid4()
    context.bed_id = str(uuid4())
    context.request = {
        "url": f"/device?gateway={context.gateway_id}&location_id={context.bed_id}&is_gateway={True}",
    }


@step("a request to get a device list with no params")
def step_impl(context):
    context.request = {
        "url": "/device",
    }


@step("several devices exist")
def step_impl(context):
    device1 = Device(
        id=context.device1_id,
        primary_identifier=context.device1_primary_identifier,
        name=context.device1_name,
        gateway_id=context.device1_id,
        location_id=context.device1_location,
        model_number="test-device",
    )
    context.db.add(device1)
    context.db.flush()
    create_alarms_and_vitals(device1, context.db)

    context.db.flush()

    device2 = Device(
        id=context.device2_id,
        primary_identifier=context.device2_primary_identifier,
        name=context.device2_name,
        gateway_id=context.device2_id,
        location_id=context.device2_location,
    )
    context.db.add(device2)
    context.db.flush()
    create_alarms_and_vitals(device2, context.db)
    context.expected_devices = [device1, device2]
    device3 = Device(
        id="b615415c-c163-4952-8794-90f6d6606836",
        primary_identifier="D-001",
        name="device",
        gateway_id="b615415c-c163-4952-8794-90f6d6606836",
    )
    context.db.add(device3)
    context.db.flush()
    create_alarms_and_vitals(device3, context.db)
    context.db.commit()


@step("a device exists with device code")
def step_impl(context):
    device1_gateway_id = uuid4()
    device2_gateway_id = uuid4()
    device1 = Device(
        id=device1_gateway_id,
        primary_identifier="PID1",
        name="DEVICE1",
        gateway_id=device1_gateway_id,
        model_number="test-device",
    )
    device2 = Device(
        id=device2_gateway_id,
        primary_identifier="PID2",
        name="DEVICE2",
        gateway_id=device2_gateway_id,
    )
    context.devices = [device1, device2]
    context.db.add(device1)
    context.db.add(device2)
    context.db.flush()
    create_alarms_and_vitals(device1, context.db)
    create_alarms_and_vitals(device2, context.db)
    context.db.commit()


@step("a device exists with gateway and location ID")
def step_impl(context):
    device1 = Device(
        id=context.gateway_id,
        primary_identifier="PID1",
        name="MONITOR",
        location_id=context.bed_id,
        gateway_id=context.gateway_id,
        audio_pause_enabled=False,
        audio_enabled=True,
    )
    context.devices = [device1]
    context.db.add(device1)
    context.db.commit()


@step("several gateways exist and a several non-gateways")
def step_impl(context):
    context.gateways = []
    for _ in range(2):
        gateway_id = uuid4()
        device = Device(
            id=gateway_id,
            primary_identifier=str(uuid4()),
            name="MONITOR",
            location_id=None,
            gateway_id=None,
        )
        context.db.add(device)
        context.gateways.append(device)

    for _ in range(2):
        device1 = Device(
            id=uuid4(),
            primary_identifier=str(uuid4()),
            name="DEVICE45",
            location_id=None,
            gateway_id=context.gateways[0].id,
        )
        context.db.add(device1)
        context.gateways.append(device1)

    context.db.commit()


@step("several gateways exist and a couple non-gateways")
def step_impl(context):
    context.gateways = []
    for _ in range(2):
        gateway_id = uuid4()
        device = Device(
            id=gateway_id,
            primary_identifier=str(uuid4()),
            name="MONITOR",
            location_id=None,
            gateway_id=None,
        )
        context.db.add(device)
        context.db.flush()
        context.gateways.append(device)
        create_alarms_and_vitals(device, context.db)

    device1 = Device(
        id=uuid4(),
        primary_identifier=str(uuid4()),
        name="DEVICE45",
        location_id=None,
        gateway_id=context.gateways[0].id,
    )
    context.db.add(device1)
    context.db.flush()
    create_alarms_and_vitals(device1, context.db)
    context.db.commit()


@step("a patient monitor with several sensors exist")
def step_impl(context):
    device1 = Device(
        id=context.gateway_id,
        primary_identifier="PID1",
        name="MONITOR",
        location_id=context.bed_id,
    )
    context.device1 = device1
    context.patient_monitor = device1
    device2 = Device(
        id=uuid4(),
        primary_identifier="PID2",
        name="DEVICE2",
        gateway_id=context.device1.id,
    )
    device3 = Device(
        id=uuid4(),
        primary_identifier="PID3",
        name="DEVICE#",
        gateway_id=context.device1.id,
    )
    context.devices = [device1, device2, device3]
    context.sensors = [device2, device3]
    context.db.add(device1)
    context.db.add(device2)
    context.db.add(device3)
    context.db.flush()
    create_alarms_and_vitals(device1, context.db)
    create_alarms_and_vitals(device2, context.db)
    create_alarms_and_vitals(device3, context.db)
    context.db.commit()


@when("the request is made to get a device list")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("the devices are returned")
def step_impl(context):
    device_map = {device.id: device for device in context.devices}
    resp = context.response.json()
    assert resp
    for device in resp["resources"]:
        assert UUID(device["id"]) in device_map
        md = device_map[UUID(device["id"])]
        assert device["primary_identifier"] == md.primary_identifier
        assert device["name"] == md.name
        assert device["location_id"] == str(md.location_id)
        assert len(md.vital_ranges) == len(device["vital_ranges"])
        assert device["audio_enabled"] is True
        assert device["audio_pause_enabled"] is False
        for actual_vital_range, expected_vital_range in zip(
            md.vital_ranges, device["vital_ranges"]
        ):
            assert str(actual_vital_range.id) == expected_vital_range["id"]
            assert actual_vital_range.code == expected_vital_range["code"]
            assert actual_vital_range.upper_limit == expected_vital_range["upper_limit"]
            assert actual_vital_range.lower_limit == expected_vital_range["lower_limit"]

        assert len(md.alerts) == len(device["alerts"])
        for actual_alert, expected_alerts in zip(md.alerts, device["alerts"]):
            assert str(actual_alert.id) == expected_alerts["id"]
            assert actual_alert.code == expected_alerts["code"]
            assert actual_alert.priority == expected_alerts["priority"]


@step("only the monitor device is returned")
def step_impl(context):
    resp = context.response.json()
    assert resp
    for device in resp["resources"]:
        md = context.device1
        assert device["id"] == md.id
        assert device["primary_identifier"] == md.primary_identifier
        assert device["name"] == md.name
        assert device["location_id"] == md.location_id
        assert len(md.vital_ranges) == len(device["vital_ranges"])
        for actual_vital_range, expected_vital_range in zip(
            md.vital_ranges, device["vital_ranges"]
        ):
            assert actual_vital_range.id == expected_vital_range["id"]
            assert actual_vital_range.code == expected_vital_range["code"]
            assert actual_vital_range.upper_limit == expected_vital_range["upper_limit"]
            assert actual_vital_range.lower_limit == expected_vital_range["lower_limit"]

        assert len(md.alerts) == len(device["alerts"])
        for actual_alert, expected_alerts in zip(md.alerts, device["alerts"]):
            assert actual_alert.id == expected_alerts["id"]
            assert actual_alert.code == expected_alerts["code"]
            assert actual_alert.priority == expected_alerts["priority"]


@step("the devices associated with filtered locations are returned")
def step_impl(context):
    resp = context.response.json()
    for index, device in enumerate(resp["resources"]):
        md = context.expected_devices[index]
        assert device["id"] == str(md.id)
        assert device["primary_identifier"] == md.primary_identifier
        assert device["name"] == md.name
        assert device["location_id"] == md.location_id
        assert device["model_number"] == md.model_number
        assert len(md.vital_ranges) == len(device["vital_ranges"])
        for actual_vital_range, expected_vital_range in zip(
            md.vital_ranges, device["vital_ranges"]
        ):
            assert str(actual_vital_range.id) == expected_vital_range["id"]
            assert actual_vital_range.code == expected_vital_range["code"]
            assert actual_vital_range.upper_limit == expected_vital_range["upper_limit"]
            assert actual_vital_range.lower_limit == expected_vital_range["lower_limit"]

        assert len(md.alerts) == len(device["alerts"])
        for actual_alert, expected_alerts in zip(md.alerts, device["alerts"]):
            assert str(actual_alert.id) == expected_alerts["id"]
            assert actual_alert.code == expected_alerts["code"]
            assert actual_alert.priority == expected_alerts["priority"]
            assert dateutil.parser.isoparse(expected_alerts["created_at"])


@step("only specific types of devices are returned")
def step_impl(context):
    resp = context.response.json()
    assert resp
    for device in resp["resources"]:
        md = context.devices[0]
        assert device["id"] == str(md.id)
        assert device["primary_identifier"] == md.primary_identifier
        assert device["name"] == md.name
        assert device["location_id"] == md.location_id
        assert device["model_number"] == md.model_number
        assert len(md.vital_ranges) == len(device["vital_ranges"])
        for actual_vital_range, expected_vital_range in zip(
            md.vital_ranges, device["vital_ranges"]
        ):
            assert str(actual_vital_range.id) == expected_vital_range["id"]
            assert actual_vital_range.code == expected_vital_range["code"]
            assert actual_vital_range.upper_limit == expected_vital_range["upper_limit"]
            assert actual_vital_range.lower_limit == expected_vital_range["lower_limit"]

        assert len(md.alerts) == len(device["alerts"])
        for actual_alert, expected_alerts in zip(md.alerts, device["alerts"]):
            assert str(actual_alert.id) == expected_alerts["id"]
            assert actual_alert.code == expected_alerts["code"]
            assert actual_alert.priority == expected_alerts["priority"]


@step("sensors are returned")
def step_impl(context):
    resp = context.response.json()
    assert resp
    devices = [context.devices[1], context.devices[2]]
    devices_map = {str(device.id): device for device in devices}

    for device in resp["resources"]:
        assert device["id"] in devices_map
        md = devices_map[device["id"]]
        assert md.name == device["name"]
        assert md.primary_identifier == device["primary_identifier"]
        assert md.location_id == device["location_id"]
        assert len(md.vital_ranges) == len(device["vital_ranges"])
        for actual_vital_range, expected_vital_range in zip(
            md.vital_ranges, device["vital_ranges"]
        ):
            assert str(actual_vital_range.id) == expected_vital_range["id"]
            assert actual_vital_range.code == expected_vital_range["code"]
            assert actual_vital_range.upper_limit == expected_vital_range["upper_limit"]
            assert actual_vital_range.lower_limit == expected_vital_range["lower_limit"]

        assert len(md.alerts) == len(device["alerts"])
        for actual_alert, expected_alerts in zip(md.alerts, device["alerts"]):
            assert str(actual_alert.id) == expected_alerts["id"]
            assert actual_alert.code == expected_alerts["code"]
            assert actual_alert.priority == expected_alerts["priority"]


@step("all the gateways are returned")
def step_impl(context):
    resp = context.response.json()
    assert resp
    devices_map = {str(device.id): device for device in context.gateways}
    for device in resp["resources"]:
        assert device["id"] in devices_map
        md = devices_map[device["id"]]
        assert md.name == device["name"]
        assert md.primary_identifier == device["primary_identifier"]
        assert (
            md.location_id is None
            and device["location_id"] is None
            or (str(md.location_id) == device["location_id"])
        )
        assert len(md.vital_ranges) == len(device["vital_ranges"])
        for actual_vital_range, expected_vital_range in zip(
            md.vital_ranges, device["vital_ranges"]
        ):
            assert str(actual_vital_range.id) == expected_vital_range["id"]
            assert actual_vital_range.code == expected_vital_range["code"]
            assert actual_vital_range.upper_limit == expected_vital_range["upper_limit"]
            assert actual_vital_range.lower_limit == expected_vital_range["lower_limit"]

        assert len(md.alerts) == len(device["alerts"])
        for actual_alert, expected_alerts in zip(md.alerts, device["alerts"]):
            assert str(actual_alert.id) == expected_alerts["id"]
            assert actual_alert.code == expected_alerts["code"]
            assert actual_alert.priority == expected_alerts["priority"]


@step("all the gateways and non-gateways are returned")
def step_impl(context):
    resp = context.response.json()
    assert resp
    devices_map = {str(device.id): device for device in context.gateways}
    assert len(resp["resources"]) == 4
    for device in resp["resources"]:
        assert device["id"] in devices_map
        md = devices_map[device["id"]]
        assert md.name == device["name"]
        assert md.primary_identifier == device["primary_identifier"]
        if device["location_id"]:
            assert str(md.location_id) == device["location_id"]
        assert len(md.vital_ranges) == len(device["vital_ranges"])
        for actual_vital_range, expected_vital_range in zip(
            md.vital_ranges, device["vital_ranges"]
        ):
            assert actual_vital_range.id == expected_vital_range["id"]
            assert actual_vital_range.code == expected_vital_range["code"]
            assert actual_vital_range.upper_limit == expected_vital_range["upper_limit"]
            assert actual_vital_range.lower_limit == expected_vital_range["lower_limit"]

        assert len(md.alerts) == len(device["alerts"])
        for actual_alert, expected_alerts in zip(md.alerts, device["alerts"]):
            assert actual_alert.id == expected_alerts["id"]
            assert actual_alert.code == expected_alerts["code"]
            assert actual_alert.priority == expected_alerts["priority"]


@step("the patient monitor and sensors are returned")
def step_impl(context):
    resp = context.response.json()
    assert resp
    found_devices_map = {str(device["id"]): device for device in resp["resources"]}
    assert len(found_devices_map.keys()) == len(context.sensors) + 1
    patient_monitor_id = str(context.patient_monitor.id)
    assert patient_monitor_id in found_devices_map
    found_patient_monitor = found_devices_map[patient_monitor_id]
    assert found_patient_monitor["name"] == context.patient_monitor.name
    assert found_patient_monitor["primary_identifier"] == context.patient_monitor.primary_identifier
    assert found_patient_monitor["location_id"] == str(context.patient_monitor.location_id)
    assert found_patient_monitor["gateway_id"] is None

    for sensor in context.sensors:
        sensor_id = str(sensor.id)
        assert sensor_id in found_devices_map
        found_sensor = found_devices_map[sensor_id]
        assert found_sensor["name"] == found_sensor.name
        assert found_sensor["primary_identifier"] == found_sensor.primary_identifier
        assert found_sensor["location_id"] is None
        assert found_sensor["gateway_id"] == patient_monitor_id

        for actual_vital_range, expected_vital_range in zip(
            found_sensor.vital_ranges, sensor["vital_ranges"]
        ):
            assert actual_vital_range.id == expected_vital_range["id"]
            assert actual_vital_range.code == expected_vital_range["code"]
            assert actual_vital_range.upper_limit == expected_vital_range["upper_limit"]
            assert actual_vital_range.lower_limit == expected_vital_range["lower_limit"]
