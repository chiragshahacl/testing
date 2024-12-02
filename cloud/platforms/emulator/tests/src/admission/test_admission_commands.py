import json
import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.admission.schemas import RejectPatientAdmissionSchema
from src.main import app
from src.settings import settings
from tests.src.monitor.factories import (
    DeviceMonitorSchemaFactory,
    PatientSchemaFactory,
)

client = TestClient(app)


@pytest.mark.asyncio
async def test_reject_patient_admission(mock_publisher, mock_start_emulation):
    # Add patient
    monitor_data = DeviceMonitorSchemaFactory().build()
    patient_data = PatientSchemaFactory().build()

    mock_publisher.add_message(
        {
            "topic": settings.KAFKA_DEVICE_TOPIC,
            "value": {
                "message_id": str(uuid.uuid4()),
                "event_type": "PATIENT_ADMISSION_REJECTED",
                "event_name": "Patient admission rejected",
                "timestamp": datetime.now().strftime(settings.TIMESTAMP_FORMAT),
                "payload": {
                    "device_primary_identifier": monitor_data.primary_identifier,
                    "patient_primary_identifier": patient_data.primary_identifier,
                },
            },
            "key": monitor_data.primary_identifier,
            "headers": [("event_type", b"PATIENT_ADMISSION_REJECTED")],
        }
    )

    payload = RejectPatientAdmissionSchema(
        patient_monitor_primary_identifier=monitor_data.primary_identifier,
        patient_primary_identifier=patient_data.primary_identifier,
    )

    response = client.post(
        url=f"{settings.BASE_PATH}/RejectAdmission",
        json=json.loads(payload.json()),
    )
    assert response.status_code == 204
    mock_publisher.assert_no_pending_messages()
