import json

from behave import step, when

from app.settings import config
from features.environment import AnyUUID
from features.steps.common import (
    CREATE_PATIENT_PARAM,
    CREATE_PATIENT_PARAM_WITHOUT_BIRTHDATE,
    assert_message_was_published,
)


@step("the create patient event is published")
def step_impl(context):
    cpp = json.loads(CREATE_PATIENT_PARAM)
    cpp.update({"event_type": "PATIENT_CREATED_EVENT", "message_id": AnyUUID()})
    topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    headers = [("event_type", b"PATIENT_CREATED_EVENT")]
    assert_message_was_published(context, topic, cpp, headers)


@step("the create patient without birthdate event is published")
def step_impl(context):
    cpp = json.loads(CREATE_PATIENT_PARAM_WITHOUT_BIRTHDATE)
    cpp.update({"event_type": "PATIENT_CREATED_EVENT", "message_id": AnyUUID()})
    topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    headers = [("event_type", b"PATIENT_CREATED_EVENT")]
    assert_message_was_published(context, topic, cpp, headers)


@when("the request is made to create a patient")
def step_impl(context):
    context.response = context.client.post(**context.request)
