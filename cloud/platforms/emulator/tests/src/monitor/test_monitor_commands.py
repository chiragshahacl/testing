import json
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.emulator import virtual_devices
from src.emulator.memory_registry import DataManager
from src.emulator.models import Patient, PatientMonitor, Sensor
from src.main import app
from src.monitor.schemas import (
    DisconnectMonitorSchema,
    PatientSessionClosedPayload,
    PatientSessionOpenedPayload,
)
from src.settings import settings
from tests.src.monitor.factories import (
    ConfigSchemaFactory,
    DeviceMonitorSchemaFactory,
    PatientSchemaFactory,
)
from tests.src.sensor.factories import (
    ConnectedSensorPayloadFactory,
    DeviceSensorSchemaFactory,
)

client = TestClient(app)


def test_connect_patient_monitor_command(mock_publisher, mock_start_emulation):
    monitor_data = DeviceMonitorSchemaFactory.build()

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
                    "patient": None,
                },
            },
            "key": monitor_data.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )
    mock_start_emulation.add_emulation(
        virtual_devices.PatientMonitor,
        None,
        monitor_data.primary_identifier,
        device_code="Patient Monitor",
        modes=None,
    )

    response = client.post(
        url=f"{settings.BASE_PATH}/monitor/ConnectPatientMonitor",
        json=json.loads(monitor_data.json()),
    )

    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
    mock_start_emulation.assert_no_pending_emulations()


def test_connect_patient_monitor_with_audio_disabled(mock_publisher, mock_start_emulation):
    device_config = ConfigSchemaFactory.build(audio_pause_enabled=False, audio_enabled=False)
    monitor_data = DeviceMonitorSchemaFactory.build(config=device_config)

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
                            "audio_enabled": False,
                        },
                        "gateway_id": None,
                    },
                    "patient": None,
                },
            },
            "key": monitor_data.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )
    mock_start_emulation.add_emulation(
        virtual_devices.PatientMonitor,
        None,
        monitor_data.primary_identifier,
        device_code="Patient Monitor",
        modes=None,
    )

    response = client.post(
        url=f"{settings.BASE_PATH}/monitor/ConnectPatientMonitor",
        json=json.loads(monitor_data.json()),
    )

    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
    mock_start_emulation.assert_no_pending_emulations()


def test_connect_patient_monitor_with_sensors_command(mock_publisher, mock_start_emulation):
    patient_data = PatientSchemaFactory().build()
    monitor_data = DeviceMonitorSchemaFactory.build(patient=patient_data)
    connected_sensor = ConnectedSensorPayloadFactory.build()
    monitor_data.connected_sensors = [connected_sensor]

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
                        "connected_sensors": [
                            {
                                "primary_identifier": connected_sensor.primary_identifier,
                                "name": connected_sensor.name,
                                "device_code": connected_sensor.device_code,
                            }
                        ],
                        "config": {
                            "audio_pause_enabled": False,
                            "audio_enabled": True,
                        },
                        "gateway_id": None,
                    },
                    "patient": {
                        "primary_identifier": monitor_data.patient.primary_identifier,
                        "given_name": monitor_data.patient.given_name,
                        "family_name": monitor_data.patient.family_name,
                        "gender": monitor_data.patient.gender,
                        "birth_date": monitor_data.patient.birth_date.isoformat(),
                    },
                },
            },
            "key": monitor_data.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )
    mock_start_emulation.add_emulation(
        virtual_devices.PatientMonitor,
        monitor_data.patient.primary_identifier,
        monitor_data.primary_identifier,
        device_code="Patient Monitor",
        modes=None,
    )

    mock_start_emulation.add_emulation(
        virtual_devices.VIRTUAL_DEVICE_CLASS_BY_CODE.get(connected_sensor.device_code),
        monitor_data.patient.primary_identifier,
        connected_sensor.primary_identifier,
        device_code=connected_sensor.device_code,
        modes=None,
    )

    response = client.post(
        url=f"{settings.BASE_PATH}/monitor/ConnectPatientMonitor",
        json=json.loads(monitor_data.json()),
    )

    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
    mock_start_emulation.assert_no_pending_emulations()


@pytest.mark.asyncio
async def test_disconnect_patient_monitor_command(mock_publisher, mock_start_emulation):
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
                    "patient": {
                        "primary_identifier": patient_data.primary_identifier,
                        "given_name": patient_data.given_name,
                        "family_name": patient_data.family_name,
                        "gender": patient_data.gender,
                        "birth_date": patient_data.birth_date.isoformat(),
                    },
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
        device_code="Patient Monitor",
        modes=None,
    )

    payload = DisconnectMonitorSchema(primary_identifier=monitor.primary_identifier)

    data_manager = DataManager()
    await data_manager.connect_patient_monitor(monitor)

    response = client.post(
        url=f"{settings.BASE_PATH}/monitor/DisconnectMonitor",
        json=json.loads(payload.json()),
    )
    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
    assert monitor.primary_identifier not in mock_start_emulation._running_devices


@pytest.mark.asyncio
async def test_disconnect_monitor_with_connected_sensor(mock_publisher, mock_start_emulation):
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
                    "patient": {
                        "primary_identifier": patient_data.primary_identifier,
                        "given_name": patient_data.given_name,
                        "family_name": patient_data.family_name,
                        "gender": patient_data.gender,
                        "birth_date": patient_data.birth_date.isoformat(),
                    },
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
                    "patient": {
                        "primary_identifier": patient_data.primary_identifier,
                        "given_name": patient_data.given_name,
                        "family_name": patient_data.family_name,
                        "gender": patient_data.gender,
                        "birth_date": patient_data.birth_date.isoformat(),
                    },
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
        device_code="Patient Monitor",
        modes=None,
    )

    mock_start_emulation.add_emulation(
        virtual_devices.VIRTUAL_DEVICE_CLASS_BY_CODE.get(sensor.device_code),
        sensor.patient.primary_identifier,
        sensor.primary_identifier,
        device_code=sensor.device_code,
        modes=None,
    )

    payload = DisconnectMonitorSchema(primary_identifier=monitor.primary_identifier)

    data_manager = DataManager()
    await data_manager.connect_patient_monitor(monitor)
    await data_manager.connect_sensor(monitor.primary_identifier, sensor)

    response = client.post(
        url=f"{settings.BASE_PATH}/monitor/DisconnectMonitor",
        json=json.loads(payload.json()),
    )
    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
    assert len(mock_start_emulation._running_devices) == 0


@pytest.mark.asyncio
async def test_open_patient_session(mock_publisher, mock_start_emulation):
    # Add patient monitor and sensor
    monitor_data = DeviceMonitorSchemaFactory().build()
    patient_data = PatientSchemaFactory().build()

    monitor = PatientMonitor(
        primary_identifier=monitor_data.primary_identifier,
        name=monitor_data.name,
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
                    "patient": None,
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
                    "patient": {
                        "primary_identifier": patient_data.primary_identifier,
                        "given_name": patient_data.given_name,
                        "family_name": patient_data.family_name,
                        "gender": patient_data.gender,
                        "birth_date": patient_data.birth_date.isoformat(),
                    },
                },
            },
            "key": monitor_data.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )

    mock_start_emulation.add_emulation(
        virtual_devices.PatientMonitor,
        None,
        monitor.primary_identifier,
        device_code=monitor.device_code,
        modes=None,
    )

    payload = PatientSessionOpenedPayload(
        patient_monitor_primary_identifier=monitor.primary_identifier,
        patient=patient_data,
    )

    data_manager = DataManager()
    await data_manager.connect_patient_monitor(monitor)

    response = client.post(
        url=f"{settings.BASE_PATH}/monitor/OpenPatientSession",
        json=json.loads(payload.json()),
    )
    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
    assert monitor.primary_identifier in mock_start_emulation._running_devices
    assert monitor.patient.primary_identifier == patient_data.primary_identifier


@pytest.mark.asyncio
async def test_close_patient_session_with_connected_sensor(mock_publisher, mock_start_emulation):
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
                    "patient": {
                        "primary_identifier": patient_data.primary_identifier,
                        "given_name": patient_data.given_name,
                        "family_name": patient_data.family_name,
                        "gender": patient_data.gender,
                        "birth_date": patient_data.birth_date.isoformat(),
                    },
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
                    "patient": {
                        "primary_identifier": patient_data.primary_identifier,
                        "given_name": patient_data.given_name,
                        "family_name": patient_data.family_name,
                        "gender": patient_data.gender,
                        "birth_date": patient_data.birth_date.isoformat(),
                    },
                },
            },
            "key": sensor_data.primary_identifier,
            "headers": [("event_type", b"DEVICE_DISCOVERED")],
        }
    )
    mock_publisher.add_message(
        {
            "topic": settings.KAFKA_DEVICE_TOPIC,
            "value": {
                "message_id": str(uuid.uuid4()),
                "event_type": "PATIENT_SESSION_CLOSED_EVENT",
                "event_name": "Patient session closed",
                "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
                "payload": {
                    "patient_primary_identifier": patient_data.primary_identifier,
                    "device_primary_identifier": monitor_data.primary_identifier,
                },
            },
            "key": patient_data.primary_identifier,
            "headers": [("event_type", b"PATIENT_SESSION_CLOSED_EVENT")],
        }
    )
    mock_start_emulation.add_emulation(
        virtual_devices.PatientMonitor,
        monitor.patient.primary_identifier,
        monitor.primary_identifier,
        device_code="Patient Monitor",
        modes=None,
    )

    mock_start_emulation.add_emulation(
        virtual_devices.VIRTUAL_DEVICE_CLASS_BY_CODE.get(sensor.device_code),
        sensor.patient.primary_identifier,
        sensor.primary_identifier,
        device_code=sensor.device_code,
        modes=None,
    )

    payload = PatientSessionClosedPayload(
        patient_monitor_primary_identifier=monitor.primary_identifier
    )

    data_manager = DataManager()
    await data_manager.connect_patient_monitor(monitor)
    await data_manager.connect_sensor(monitor.primary_identifier, sensor)

    response = client.post(
        url=f"{settings.BASE_PATH}/monitor/ClosePatientSession",
        json=json.loads(payload.json()),
    )
    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
    assert monitor.primary_identifier in mock_start_emulation._running_devices
    assert sensor.primary_identifier not in mock_start_emulation._running_devices
