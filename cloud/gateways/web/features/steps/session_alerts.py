import json

import respx
from behave import step
from httpx import Response
from starlette import status
from test_tools import assert_deep_equal

from src.patient.schemas import WebSessionAlertResources
from src.settings import settings


@step("the patient's device has technical alerts")
def set_technical_alerts(context):
    context.technical_alerts = [
        {
            "code": "technical-code1",
            "start_determination_time": "2024-01-01T12:00:00",
            "end_determination_time": "2024-01-01T12:30:00",
            "value_text": "value1",
            "device_primary_identifier": "device-pid1",
            "device_code": "device-code",
        },
        {
            "code": "technical-code2",
            "start_determination_time": "2024-01-01T13:00:00",
            "end_determination_time": "2024-01-01T13:30:00",
            "value_text": "value2",
            "device_primary_identifier": "device-pid2",
            "device_code": "device-code",
        },
        {
            "code": "technical-code3",
            "start_determination_time": "2024-01-01T14:00:00",
            "end_determination_time": "2024-01-01T14:30:00",
            "value_text": "value3",
            "device_primary_identifier": "device-pid3",
            "device_code": "device-code",
        },
    ]


@step("the patient has alerts physiological alerts")
def set_physiolocical_alerts(context):
    context.physiological_alerts = [
        {
            "code": "physiological-code1",
            "start_determination_time": "2024-01-01T10:00:00",
            "end_determination_time": "2024-01-01T10:30:00",
            "value_text": "value1",
            "device_primary_identifier": "device-pid1",
            "device_code": "device-code",
            "trigger_upper_limit": 120,
            "trigger_lower_limit": 80,
        },
        {
            "code": "physiological-code2",
            "start_determination_time": "2024-01-01T11:00:00",
            "end_determination_time": "2024-01-01T11:30:00",
            "value_text": "value2",
            "device_primary_identifier": "device-pid2",
            "device_code": "device-code",
            "trigger_upper_limit": 100,
            "trigger_lower_limit": 60,
        },
        {
            "code": "physiological-code3",
            "start_determination_time": "2024-01-01T15:00:00",
            "end_determination_time": "2024-01-01T15:30:00",
            "value_text": "value3",
            "device_primary_identifier": "device-pid3",
            "device_code": "device-code",
            "trigger_upper_limit": 80,
            "trigger_lower_limit": 30,
        },
    ]


@step("a request is set to get a patient physiological alerts")
def set_request_physiological_alerts(context):
    id = context.patient["id"]
    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/{id}/session/alerts",
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json=context.physiological_alerts,
        )
    )


@step("a request to get session alerts")
def set_request_session_alerts(context):
    id = context.patient["id"]
    context.request = {"url": f"/web/patient/{id}/session/alerts"}


@step("the request to get session alerts is made")
def request_alerts(context):
    context.response = context.client.get(**context.request)


@step("the expected response is returned")
def check_session_response(context):
    actual = context.response.json()
    resources = sorted(
        context.physiological_alerts, key=lambda k: k["start_determination_time"], reverse=True
    )

    expected = WebSessionAlertResources(resources=resources)

    assert_deep_equal(actual, json.loads(expected.model_dump_json(by_alias=True)))
