import json
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.emulator import virtual_devices
from src.emulator.memory_registry import DataManager
from src.emulator.models import Patient, PatientMonitor, Sensor
from src.main import app
from src.monitor.schemas import PatientMonitorResourcesSchema
from src.settings import settings
from tests.src.monitor.factories import DeviceMonitorSchemaFactory, PatientSchemaFactory
from tests.src.sensor.factories import DeviceSensorSchemaFactory

client = TestClient(app)


@pytest.mark.asyncio
async def test_get_patient_monitor_list(mock_publisher, mock_start_emulation):
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

    data_manager = DataManager()
    await data_manager.connect_patient_monitor(monitor)
    await data_manager.connect_sensor(monitor.primary_identifier, sensor)

    response = client.get(
        url=f"{settings.BASE_PATH}/monitor/",
    )

    assert response.status_code == 200
    assert PatientMonitorResourcesSchema(**response.json())
