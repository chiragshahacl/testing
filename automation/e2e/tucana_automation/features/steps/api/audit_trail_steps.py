import json
import time
import uuid

from behave import *
from faker import Faker

from features.steps.api.common_api_steps import verify_delete_request_status
from utils.api_utils import (
    requests_delete,
    requests_delete_batch,
    requests_get,
    requests_post,
    requests_put,
)


@step("the user wants to get the audit trail for the recently created patient")
def get_audit_trail(context):
    url = "/web/audit/" + context.patient_id
    context.response = requests_get(context, url)


@step("the user wants to get the audit trail for the recently created bed")
def get_audit_trail(context):
    url = "/web/audit/" + context.bed_id
    context.response = requests_get(context, url)


@step("the user wants to get the audit trail for the recently created bed group")
def get_audit_trail(context):
    url = "/web/audit/" + context.bed_group_id
    context.response = requests_get(context, url)


@step("the user verifies that all the patient audit trail information is correct")
def verify_patient_information(context):
    patient_audit_trail = context.response.json()
    assert patient_audit_trail["resources"][0]["entity_id"] == context.patient_id, (
        "Expected UUID "
        + context.patient_id
        + " current "
        + patient_audit_trail["resources"][0]["entity_id"]
    )
    assert patient_audit_trail["resources"][0]["event_name"] == "Patient Created", (
        "Expected event name "
        + "Patient Created"
        + " current "
        + patient_audit_trail["resources"][0]["event_name"]
    )
    assert (
        "timestamp" in patient_audit_trail["resources"][0]
    ), "The timestamp field is not present in response"
    assert (
        patient_audit_trail["resources"][0]["data"]["current_state"]["id"]
        == context.patient_id
    ), (
        "Expected UUID "
        + context.patient_id
        + " current "
        + patient_audit_trail["resources"][0]["data"]["current_state"]["id"]
    )
    assert (
        patient_audit_trail["resources"][0]["data"]["current_state"][
            "primary_identifier"
        ]
        == context.patient_identifier
    ), (
        "Expected Identifier "
        + context.patient_identifier
        + " current "
        + patient_audit_trail["resources"][0]["data"]["current_state"][
            "primary_identifier"
        ]
    )
    assert (
        patient_audit_trail["resources"][0]["data"]["current_state"]["active"]
        == context.active
    ), (
        "Expected Status "
        + context.active
        + " current "
        + patient_audit_trail["resources"][0]["data"]["current_state"]["active"]
    )
    assert (
        patient_audit_trail["resources"][0]["data"]["current_state"]["given_name"]
        == context.patient_given_name
    ), (
        "Expected First Name "
        + context.patient_given_name
        + " current "
        + patient_audit_trail["resources"][0]["data"]["current_state"]["given_name"]
    )

    assert (
        patient_audit_trail["resources"][0]["data"]["current_state"]["family_name"]
        == context.patient_family_name
    ), (
        "Expected Last Name "
        + context.patient_family_name
        + " current "
        + patient_audit_trail["resources"][0]["data"]["current_state"]["family_name"]
    )

    assert (
        patient_audit_trail["resources"][0]["data"]["current_state"]["gender"]
        == context.patient_gender[0]
    ), (
        "Expected Gender "
        + context.patient_gender[0]
        + " current "
        + patient_audit_trail["resources"][0]["data"]["current_state"]["gender"]
    )
    assert (
        patient_audit_trail["resources"][0]["data"]["current_state"]["birth_date"]
        == context.birth_date
    ), (
        "patient birth date doesn't match, expected "
        + context.birth_date
        + " current "
        + patient_audit_trail["resources"][0]["data"]["current_state"]["birth_date"]
    )


@step("the user verifies that all the bed group audit trail information is correct")
def verify_bed_group_information(context):
    bed_group_audit_trail = context.response.json()
    assert bed_group_audit_trail["resources"][0]["entity_id"] == context.bed_group_id, (
        "Expected UUID "
        + context.bed_group_id
        + " current "
        + bed_group_audit_trail["resources"][0]["entity_id"]
    )
    assert bed_group_audit_trail["resources"][0]["event_name"] == "Bed group created", (
        "Expected event name "
        + "Bed group created"
        + " current "
        + bed_group_audit_trail["resources"][0]["event_name"]
    )
    assert (
        "timestamp" in bed_group_audit_trail["resources"][0]
    ), "The timestamp field is not present in response"
    assert (
        bed_group_audit_trail["resources"][0]["data"]["current_state"]["id"]
        == context.bed_group_id
    ), (
        "Expected UUID "
        + context.bed_group_id
        + " current "
        + bed_group_audit_trail["resources"][0]["data"]["current_state"]["id"]
    )
    assert (
        bed_group_audit_trail["resources"][0]["data"]["current_state"]["name"]
        == context.bed_group_name
    ), (
        "The bed groups name doesn't match, expected "
        + context.bed_group_name
        + " current "
        + bed_group_audit_trail["resources"][0]["data"]["current_state"]["name"]
    )
    assert (
        bed_group_audit_trail["resources"][0]["data"]["current_state"]["description"]
        == context.bed_group_description
    ), (
        "The bed groups description doesn't match, expected "
        + context.bed_group_description
        + " current "
        + bed_group_audit_trail["resources"][0]["data"]["current_state"]["description"]
    )


@step("the user verifies that all the bed audit trail information is correct")
def verify_bed_information(context):
    bed_audit_trail = context.response.json()
    assert bed_audit_trail["resources"][0]["entity_id"] == context.bed_id, (
        "Expected UUID "
        + context.bed_id
        + " current "
        + bed_audit_trail["resources"][0]["entity_id"]
    )
    assert bed_audit_trail["resources"][0]["event_name"] == "Bed created", (
        "Expected event name "
        + "Bed created"
        + " current "
        + bed_audit_trail["resources"][0]["event_name"]
    )
    assert (
        "timestamp" in bed_audit_trail["resources"][0]
    ), "The timestamp field is not present in response"
    assert (
        bed_audit_trail["resources"][0]["data"]["current_state"]["id"] == context.bed_id
    ), (
        "The bed id doesn't match, expected "
        + context.bed_id
        + " current "
        + bed_audit_trail["resources"][0]["data"]["current_state"]["id"]
    )
    assert (
        bed_audit_trail["resources"][0]["data"]["current_state"]["name"]
        == context.bed_name
    ), (
        "The bed name doesn't match, expected "
        + context.bed_name
        + " current "
        + bed_audit_trail["resources"][0]["data"]["current_state"]["name"]
    )
