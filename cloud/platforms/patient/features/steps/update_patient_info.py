from behave import step, when

from app.settings import config
from features.environment import AnyDateTime, AnyUUID
from features.steps.common import assert_message_was_published


@step("a request to update a patient")
def step_impl(context):
    context.patient_id = "7ab46f31-c98d-4c19-b720-798972787459"
    context.patient_primary_identifier = "primary-identifier"
    context.patient_active = True
    context.patient_given_name = "given"
    context.patient_family_name = "family"
    context.patient_gender = "male"
    context.birth_date = "2020-03-29"
    context.request = {
        "url": "/patient/UpdatePatientInfo",
        "json": {
            "id": context.patient_id,
            "primary_identifier": context.patient_primary_identifier,
            "active": context.patient_active,
            "given_name": context.patient_given_name,
            "family_name": context.patient_family_name,
            "gender": context.patient_gender,
            "birth_date": context.birth_date,
        },
    }


@when("the request is made to update a patient")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the update patient event is published")
def step_impl(context):
    topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    value = {
        "entity_id": "7ab46f31-c98d-4c19-b720-798972787459",
        "event_name": "Patient personal information updated",
        "performed_on": AnyDateTime(),
        "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "event_state": {
            "id": "7ab46f31-c98d-4c19-b720-798972787459",
            "primary_identifier": "primary-identifier",
            "active": False,
            "given_name": "new-given-name",
            "family_name": "new-family-name",
            "gender": "other",
            "birth_date": "2021-03-29",
        },
        "previous_state": {
            "id": "7ab46f31-c98d-4c19-b720-798972787459",
            "primary_identifier": "primary-identifier",
            "active": True,
            "given_name": "given",
            "family_name": "family",
            "gender": "male",
            "birth_date": "2020-03-29",
        },
        "entity_name": "patient",
        "emitted_by": "patient",
        "event_type": "UPDATE_PATIENT_INFO_EVENT",
        "message_id": AnyUUID(),
        "event_data": {
            "primary_identifier": "primary-identifier",
            "active": False,
            "given_name": "new-given-name",
            "family_name": "new-family-name",
            "gender": "other",
            "birth_date": "2021-03-29",
        },
    }
    headers = [("event_type", b"UPDATE_PATIENT_INFO_EVENT")]

    assert_message_was_published(context, topic, value, headers)
