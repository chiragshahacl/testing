import json
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.emulator import virtual_devices
from src.emulator.constants import (
    DeviceEmulationModes,
    DeviceEmulationNames,
    DeviceTypes,
)
from src.emulator.memory_registry import DataManager
from src.emulator.models import Patient, PatientMonitor, Sensor
from src.main import app
from src.sensor.schemas import DisconnectSensorSchema
from src.settings import settings
from tests.src.monitor.factories import DeviceMonitorSchemaFactory, PatientSchemaFactory
from tests.src.sensor.factories import (
    DeviceSensorSchemaFactory,
    UpdateSensorModeWebSchemaFactory,
)

client = TestClient(app)


@pytest.mark.asyncio
async def test_connect_sensor_command(mock_publisher, mock_start_emulation):
    # Add patient monitor
    monitor_data = DeviceMonitorSchemaFactory().build()
    patient_data = PatientSchemaFactory().build()

    patient = Patient(
        primary_identifier=patient_data.primary_identifier,
        given_name=patient_data.given_name,
        family_name=patient_data.family_name,
        gender=patient_data.gender,
        birth_date=patient_data.birth_date,
    )
    monitor = PatientMonitor(
        primary_identifier=monitor_data.primary_identifier,
        name=monitor_data.name,
        patient=patient,
    )
    # Set the patient monitor primary identifier as sensor gateway
    payload = DeviceSensorSchemaFactory.build(
        patient_monitor_primary_identifier=monitor.primary_identifier
    )

    mock_publisher.add_message(
        {
            "topic": settings.KAFKA_DEVICE_TOPIC,
            "value": {
                "message_id": str(uuid.uuid4()),
                "event_type": "DEVICE_DISCOVERED",
                "event_name": "Device discovered",
                "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
                "payload": {
                    "device": {
                        "primary_identifier": monitor_data.primary_identifier,
                        "name": monitor_data.name,
                        "device_code": "Patient Monitor",
                        "connected_sensors": None,
                        "config": {
                            "audio_pause_enabled": False,
                            "audio_enabled": True,
                        },
                        "gateway_id": None,
                    },
                    "patient": json.loads(patient_data.json()),
                },
            },
            "key": monitor_data.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )
    mock_start_emulation.add_emulation(
        virtual_devices.PatientMonitor,
        monitor.patient.primary_identifier,
        monitor.primary_identifier,
        device_code=monitor.device_code,
        modes=None,
    )
    mock_publisher.add_message(
        {
            "topic": settings.KAFKA_DEVICE_TOPIC,
            "value": {
                "message_id": str(uuid.uuid4()),
                "event_type": "DEVICE_DISCOVERED",
                "event_name": "Device discovered",
                "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
                "payload": {
                    "device": {
                        "primary_identifier": payload.primary_identifier,
                        "name": payload.name,
                        "device_code": payload.device_code,
                        "connected_sensors": None,
                        "config": {
                            "audio_pause_enabled": False,
                            "audio_enabled": True,
                        },
                        "gateway_id": payload.patient_monitor_primary_identifier,
                    },
                    "patient": json.loads(patient_data.json()),
                },
            },
            "key": payload.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )
    mock_start_emulation.add_emulation(
        virtual_devices.VIRTUAL_DEVICE_CLASS_BY_CODE.get(payload.device_code),
        monitor.patient.primary_identifier,
        payload.primary_identifier,
        device_code=payload.device_code,
        modes=None,
    )

    data_manager = DataManager()
    await data_manager.connect_patient_monitor(monitor)

    response = client.post(
        url=f"{settings.BASE_PATH}/sensor/ConnectSensor",
        json=json.loads(payload.json()),
    )

    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
    mock_start_emulation.assert_no_pending_emulations()


@pytest.mark.asyncio
async def test_update_sensor_mode_command(mock_publisher, mock_start_emulation):
    # Add patient monitor and sensor
    monitor_data = DeviceMonitorSchemaFactory().build()
    patient_data = PatientSchemaFactory().build()
    sensor_data = DeviceSensorSchemaFactory.build(device_code=DeviceTypes.ANNE_CHEST)

    patient = Patient(
        primary_identifier=patient_data.primary_identifier,
        given_name=patient_data.given_name,
        family_name=patient_data.family_name,
        gender=patient_data.gender,
        birth_date=patient_data.birth_date,
    )
    monitor = PatientMonitor(
        primary_identifier=monitor_data.primary_identifier,
        name=monitor_data.name,
        patient=patient,
    )
    sensor = Sensor(
        primary_identifier=sensor_data.primary_identifier,
        name=sensor_data.name,
        device_code=sensor_data.device_code,
        patient=monitor.patient,
        patient_monitor=monitor,
    )

    mock_publisher.add_message(
        {
            "topic": settings.KAFKA_DEVICE_TOPIC,
            "value": {
                "message_id": str(uuid.uuid4()),
                "event_type": "DEVICE_DISCOVERED",
                "event_name": "Device discovered",
                "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
                "payload": {
                    "device": {
                        "primary_identifier": monitor_data.primary_identifier,
                        "name": monitor_data.name,
                        "device_code": "Patient Monitor",
                        "connected_sensors": None,
                        "config": {
                            "audio_pause_enabled": False,
                            "audio_enabled": True,
                        },
                        "gateway_id": None,
                    },
                    "patient": json.loads(patient_data.json()),
                },
            },
            "key": monitor_data.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )

    mock_publisher.add_message(
        {
            "topic": settings.KAFKA_DEVICE_TOPIC,
            "value": {
                "message_id": str(uuid.uuid4()),
                "event_type": "DEVICE_DISCOVERED",
                "event_name": "Device discovered",
                "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
                "payload": {
                    "device": {
                        "primary_identifier": sensor_data.primary_identifier,
                        "name": sensor_data.name,
                        "device_code": sensor_data.device_code,
                        "connected_sensors": None,
                        "config": {
                            "audio_pause_enabled": False,
                            "audio_enabled": True,
                        },
                        "gateway_id": monitor_data.primary_identifier,
                    },
                    "patient": json.loads(patient_data.json()),
                },
            },
            "key": sensor_data.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )
    mock_start_emulation.add_emulation(
        virtual_devices.PatientMonitor,
        monitor.patient.primary_identifier,
        monitor.primary_identifier,
        device_code=monitor.device_code,
        modes=None,
    )

    mock_start_emulation.add_emulation(
        virtual_devices.VIRTUAL_DEVICE_CLASS_BY_CODE.get(sensor.device_code),
        sensor.patient.primary_identifier,
        sensor.primary_identifier,
        device_code=sensor.device_code,
        modes=None,
    )

    payload = UpdateSensorModeWebSchemaFactory.build(
        primary_identifier=sensor.primary_identifier,
        emulator_name=DeviceEmulationNames.CARDIAC.value,
        mode=DeviceEmulationModes.HIGH.value,
    )

    data_manager = DataManager()
    await data_manager.connect_patient_monitor(monitor)
    await data_manager.connect_sensor(monitor.primary_identifier, sensor)

    mock_start_emulation.add_emulation(
        virtual_devices.VIRTUAL_DEVICE_CLASS_BY_CODE.get(sensor.device_code),
        sensor.patient.primary_identifier,
        sensor.primary_identifier,
        device_code=sensor.device_code,
        modes={DeviceEmulationNames.CARDIAC: DeviceEmulationModes.HIGH},
    )

    response = client.post(
        url=f"{settings.BASE_PATH}/sensor/UpdateSensorMode",
        json=json.loads(payload.json()),
    )
    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
    mock_start_emulation.assert_no_pending_emulations()


@pytest.mark.asyncio
async def test_disconnect_sensor_command(mock_publisher, mock_start_emulation):
    # Add patient monitor and sensor
    monitor_data = DeviceMonitorSchemaFactory().build()
    patient_data = PatientSchemaFactory().build()
    sensor_data = DeviceSensorSchemaFactory.build()

    patient = Patient(
        primary_identifier=patient_data.primary_identifier,
        given_name=patient_data.given_name,
        family_name=patient_data.family_name,
        gender=patient_data.gender,
        birth_date=patient_data.birth_date,
    )
    monitor = PatientMonitor(
        primary_identifier=monitor_data.primary_identifier,
        name=monitor_data.name,
        patient=patient,
    )
    sensor = Sensor(
        primary_identifier=sensor_data.primary_identifier,
        name=sensor_data.name,
        device_code=sensor_data.device_code,
        patient=monitor.patient,
        patient_monitor=monitor,
    )

    mock_publisher.add_message(
        {
            "topic": settings.KAFKA_DEVICE_TOPIC,
            "value": {
                "message_id": str(uuid.uuid4()),
                "event_type": "DEVICE_DISCOVERED",
                "event_name": "Device discovered",
                "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
                "payload": {
                    "device": {
                        "primary_identifier": monitor_data.primary_identifier,
                        "name": monitor_data.name,
                        "device_code": "Patient Monitor",
                        "connected_sensors": None,
                        "config": {
                            "audio_pause_enabled": False,
                            "audio_enabled": True,
                        },
                        "gateway_id": None,
                    },
                    "patient": json.loads(patient_data.json()),
                },
            },
            "key": monitor_data.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )

    mock_publisher.add_message(
        {
            "topic": settings.KAFKA_DEVICE_TOPIC,
            "value": {
                "message_id": str(uuid.uuid4()),
                "event_type": "DEVICE_DISCOVERED",
                "event_name": "Device discovered",
                "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
                "payload": {
                    "device": {
                        "primary_identifier": sensor_data.primary_identifier,
                        "name": sensor_data.name,
                        "device_code": sensor_data.device_code,
                        "connected_sensors": None,
                        "config": {
                            "audio_pause_enabled": False,
                            "audio_enabled": True,
                        },
                        "gateway_id": monitor_data.primary_identifier,
                    },
                    "patient": json.loads(patient_data.json()),
                },
            },
            "key": sensor_data.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )
    mock_start_emulation.add_emulation(
        virtual_devices.PatientMonitor,
        monitor.patient.primary_identifier,
        monitor.primary_identifier,
        device_code=monitor.device_code,
        modes=None,
    )

    mock_start_emulation.add_emulation(
        virtual_devices.VIRTUAL_DEVICE_CLASS_BY_CODE.get(sensor.device_code),
        sensor.patient.primary_identifier,
        sensor.primary_identifier,
        device_code=sensor.device_code,
        modes=None,
    )

    mock_publisher.add_message(
        {
            "topic": settings.KAFKA_DEVICE_TOPIC,
            "value": {
                "message_id": str(uuid.uuid4()),
                "event_type": "SENSOR_REMOVED_EVENT",
                "event_name": "Sensor removed",
                "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
                "payload": {
                    "device_primary_identifier": sensor_data.primary_identifier,
                    "device_type": sensor.device_code,
                    "patient_primary_identifier": patient_data.primary_identifier,
                    "determination_time": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
                },
            },
            "key": sensor_data.primary_identifier,
            "headers": [("event_type", b"SENSOR_REMOVED_EVENT")],
        }
    )

    payload = DisconnectSensorSchema(
        primary_identifier=sensor.primary_identifier,
    )

    data_manager = DataManager()
    await data_manager.connect_patient_monitor(monitor)
    await data_manager.connect_sensor(monitor.primary_identifier, sensor)

    response = client.post(
        url=f"{settings.BASE_PATH}/sensor/DisconnectSensor",
        json=json.loads(payload.json()),
    )
    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
    assert sensor.primary_identifier not in mock_start_emulation._running_devices
