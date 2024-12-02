import json
import uuid

from behave import *
from faker import Faker

from features.steps.api.common_api_steps import verify_delete_request_status, authentication_included, request_success, \
    verify_request_status
from features.steps.api.emulator import create_patient_for_emulators
from utils.api_utils import (
    requests_delete,
    requests_delete_batch,
    requests_get,
    requests_post,
    requests_put, set_alarm_to_patient,
)
from features.steps.common import parse_text


@step("A request to create a new patient through Tucana's API")
@step('a request to create a patient with invalid gender "{gender}" in payload')
@step("A request to create a new patient through upsert endpoint")
def create_new_patient(context, gender="true"):
    faker = Faker()
    context.patient_id = str(uuid.uuid1())
    context.patient_identifier = faker.bothify("APAT-####-??", letters="ABCDE")
    if gender == "true":
        context.patient_gender = faker.random_elements(
            elements=("female", "male"), length=1
        )
        if context.patient_gender[0] == "male":
            context.patient_given_name = faker.first_name_male()
            context.patient_family_name = faker.last_name()
        else:
            context.patient_given_name = faker.first_name_female()
            context.patient_family_name = faker.last_name()
    else:
        context.patient_gender = gender
        context.patient_given_name = faker.first_name_male()
        context.patient_family_name = faker.last_name()
    context.identifier = [{"value": context.patient_id}]
    context.active = True
    context.birth_date = faker.date()
    context.data = {
        "url": "/web/patient",
        "json": {
            "id": context.patient_id,
            "primary_identifier": context.patient_identifier,
            "active": context.active,
            "given_name": context.patient_given_name,
            "family_name": context.patient_family_name,
            "gender": context.patient_gender[0],
            "birth_date": context.birth_date,
        },
    }


@step("the request is made to create a patient")
def send_new_patient_request(context):
    url = context.data["url"]
    context.response = requests_post(context, url, context.data["json"], headers=None)


@step("the user wants to get the recently created user")
def get_patient_by_id(context):
    url = "web/patient/" + context.patient_id
    context.response = requests_get(context, url)


@step("the patient is created")
def verify_patient_created(context):
    patient_created = context.response.json()
    context.patient_id = patient_created["id"]
    assert patient_created["primary_identifier"] == context.patient_identifier, (
            "The patient identifier ID doesn't match, expected "
            + context.patient_identifier
            + " current "
            + patient_created["'primary_identifier'"]
    )
    assert patient_created["active"] == context.active, (
            "patient active doesn't match, expected "
            + context.active
            + " current "
            + patient_created["active"]
    )
    assert patient_created["gender"] == context.patient_gender[0], (
            "patient gender doesn't match, expected "
            + context.patient_gender[0]
            + " current "
            + patient_created["gender"]
    )
    assert patient_created["given_name"] == context.patient_given_name, (
            "patient given name doesn't match, expected "
            + context.patient_given_name
            + " current "
            + patient_created["given_name"]
    )
    assert patient_created["family_name"] == context.patient_family_name, (
            "patient family name doesn't match, expected "
            + context.patient_family_name
            + " current "
            + patient_created["family_name"]
    )
    assert patient_created["birth_date"] == context.birth_date, (
            "patient birth date doesn't match, expected "
            + context.birth_date
            + " current "
            + patient_created["birth_date"]
    )


@step("The patient is removed to keep the application clean")
def remove_patient_clean_application(context):
    context.response = requests_delete(
        context, "web/patient/{}".format(context.patient_id), headers=None
    )
    verify_delete_request_status(context)


@step("the user verifies that all the Patient information is correct")
def verify_patient_information(context):
    patient_data = json.loads(context.response.text)
    context.patient_id = patient_data["id"]
    assert patient_data["id"] == context.patient_id, (
            "Expected UUID " + context.patient_id + " current " + patient_data["id"]
    )
    assert patient_data["primaryIdentifier"] == context.patient_identifier, (
            "Expected Identifier "
            + context.patient_identifier
            + " current "
            + patient_data["primaryIdentifier"]
    )
    assert patient_data["active"] == context.active, (
            "Expected Status " + context.active + " current " + patient_data["active"]
    )
    assert patient_data["givenName"] == context.patient_given_name, (
            "Expected First Name "
            + context.patient_given_name
            + " current "
            + patient_data["givenName"]
    )
    assert patient_data["familyName"] == context.patient_family_name, (
            "Expected Last Name "
            + context.patient_family_name
            + " current "
            + patient_data["familyName"]
    )
    assert patient_data["gender"] == context.patient_gender[0], (
            "Expected Gender "
            + context.patient_gender[0]
            + " current "
            + patient_data["gender"]
    )
    assert patient_data["birthDate"] == context.birth_date, (
            "patient birth date doesn't match, expected "
            + context.birth_date
            + " current "
            + patient_data["birthDate"]
    )


@step("some patient exist")
def some_patient_exist(context):
    context.patients_ids = []
    context.patients_created = []
    create_patients = 2
    for i in range(create_patients):
        context.execute_steps(
            """
                Given A request to create a new patient through Tucana's API
                And A request to create a new patient through Tucana's API
                When the request is made to create a patient
                Then the user is told the request to create was successful
                And the patient is created
            """
        )
        context.patients_ids.append(context.patient_id)
        context.patients_created.append(context.response.json())


@step("the user wants to get the list of patients")
def get_patient_list(context):
    url = "/web/patient"
    context.response = requests_get(context, url)


@step("patient list is received")
def verify_patient_list(context):
    patient_list = context.response.json()
    patients_created = context.patients_created
    context.patient_ids = []
    for index, payload_entry in enumerate(patient_list["resources"]):
        for index1, payload in enumerate(patients_created):
            payload_patient_id = patient_list["resources"][index]["id"]
            existing_patient_id = patients_created[index1]["id"]
            if payload_patient_id == existing_patient_id:
                # context.beds_ids.append(existing_patient_id)
                assert (
                        patient_list["resources"][index]["primaryIdentifier"]
                        == patients_created[index1]["primary_identifier"]
                ), (
                        "The patient primary identifier doesn't match, expected "
                        + patients_created[index1]["primary_identifier"]
                        + " current "
                        + patient_list["resources"][index]["primaryIdentifier"]
                )
                assert (
                        patient_list["resources"][index]["active"]
                        == patients_created[index1]["active"]
                ), (
                        "The patient status doesn't match, expected "
                        + patients_created[index1]["active"]
                        + " current "
                        + patient_list["resources"][index]["active"]
                )
                assert (
                        patient_list["resources"][index]["givenName"]
                        == patients_created[index1]["given_name"]
                ), (
                        "The patient given name doesn't match, expected "
                        + patients_created[index1]["given_name"]
                        + " current "
                        + patient_list["resources"][index]["givenName"]
                )
                assert (
                        patient_list["resources"][index]["familyName"]
                        == patients_created[index1]["family_name"]
                ), (
                        "The patient given name doesn't match, expected "
                        + patients_created[index1]["family_name"]
                        + " current "
                        + patient_list["resources"][index]["familyName"]
                )
                assert (
                        patient_list["resources"][index]["gender"]
                        == patients_created[index1]["gender"]
                ), (
                        "The patient gender doesn't match, expected "
                        + patients_created[index1]["gender"]
                        + " current "
                        + patient_list["resources"][index]["gender"]
                )
                assert (
                        patient_list["resources"][index]["birthDate"]
                        == patients_created[index1]["birth_date"]
                ), (
                        "The patient birth date doesn't match, expected "
                        + patients_created[index1]["birth_date"]
                        + " current "
                        + patient_list["resources"][index]["birthDate"]
                )


@step("patients are removed to keep the application clean")
def remove_patients_clean_application(context):
    for index, payload_entry in enumerate(context.patients_ids):
        context.response = requests_delete(
            context, "web/patient/{}".format(context.patients_ids[index]), headers=None
        )
        verify_delete_request_status(context)


@step("the request is made to create a patient through upsert endpoint")
@step("the request is made to update a patient through upsert endpoint")
def send_new_patient_request(context):
    url = context.data["url"]
    context.response = requests_put(context, url, context.data["json"], headers=None)


@step("the patient exist")
def the_patient_exist(context):
    context.execute_steps(
        """
            Given A request to create a new patient through Tucana's API
            And A request to create a new patient through Tucana's API
            When the request is made to create a patient
            Then the user is told the request to create was successful
            And the patient is created
        """
    )


@step("A request to update a patient through upsert endpoint")
def create_patient(context, gender="true"):
    faker = Faker()
    if gender == "true":
        context.patient_gender = faker.random_elements(
            elements=("female", "male"), length=1
        )
        if context.patient_gender[0] == "male":
            context.patient_given_name = faker.first_name_male()
            context.patient_family_name = faker.last_name()
        else:
            context.patient_given_name = faker.first_name_female()
            context.patient_family_name = faker.last_name()
    else:
        context.patient_gender = gender
        context.patient_given_name = faker.first_name_male()
        context.patient_family_name = faker.last_name()
    context.identifier = [{"value": context.patient_id}]
    context.active = True
    context.birth_date = faker.date()
    context.data = {
        "url": "/web/patient",
        "json": {
            "id": context.patient_id,
            "primary_identifier": context.patient_identifier,
            "active": context.active,
            "given_name": context.patient_given_name,
            "family_name": context.patient_family_name,
            "gender": context.patient_gender[0],
            "birth_date": context.birth_date,
        },
    }


@step('the user wants to get the EHR patient by "{}"')
def get_ehr_patient_by_id(context, parameter):
    if parameter == "patientIdentifier":
        url = "web/patient/ehr?patientIdentifier=" + str(context.patient_ehr_data['patient']['primary_patient_id'])
    elif parameter == "givenName" or parameter == "familyName":
        url = "web/patient/ehr?givenName=" + context.patient_ehr_data['patient']['given_name'] + "&familyName=" + \
              context.patient_ehr_data['patient']['family_name']
    elif parameter == "birthDate":
        url = "web/patient/ehr?patientIdentifier=" + str(
            context.patient_ehr_data['patient']['primary_patient_id']) + "&birthDate=" + str(
            context.patient_ehr_data['patient']['dob'])
    context.response = requests_get(context, url)


@step("The patient from EHR exists with the following data")
def patient_from_ehr(context):
    context.patient_ehr_data = parse_text(context)


@step("the user verifies that the EHR Patient information is correct")
def verify_ehr_patient_information(context):
    ehr_patient_response = context.response.json()
    assert ehr_patient_response["resources"][0]["givenName"] == context.patient_ehr_data['patient']['given_name'], (
            "Expected Last Name "
            + context.patient_ehr_data['patient']['given_name']
            + " current "
            + ehr_patient_response["resources"][0]["givenName"]
    )
    assert ehr_patient_response["resources"][0]["familyName"] == context.patient_ehr_data['patient']['family_name'], (
            "Expected Last Name "
            + context.patient_ehr_data['patient']['family_name']
            + " current "
            + ehr_patient_response["resources"][0]["familyName"]
    )
    assert ehr_patient_response["resources"][0]["birthDate"] == str(context.patient_ehr_data['patient']["dob"]), (
            "The patient birth date doesn't match, expected "
            + ehr_patient_response["resources"][0]["birthDate"]
            + " current "
            + context.patient_ehr_data['patient']["dob"]
    )


@step("Tom wants to get the patient session alerts")
def get_patient_session_alerts(context):
    url = "/web/patient/" + context.patient_bed_and_group["patient"] + "/session/alerts"
    context.response = requests_get(context, url)


@step("Tom verifies that the patient session alerts information is correct")
def verify_patient_session_alerts(context):
    patient_session_alerts_response = context.response.json()
    assert patient_session_alerts_response["resources"][0]["code"] == context.alarm_code, (
            "Expected alarm code "
            + patient_session_alerts_response["resources"][0]["code"]
            + " current "
            + context.alarm_code
    )
    assert patient_session_alerts_response["resources"][0]["deviceCode"] == context.device_code, (
            "Expected device code "
            + patient_session_alerts_response["resources"][0]["deviceCode"]
            + " current "
            + context.device_code
    )
    assert patient_session_alerts_response["resources"][0]["devicePrimaryIdentifier"] == context.sensor_type, (
            "Expected device primary identifier "
            + patient_session_alerts_response["resources"][0]["devicePrimaryIdentifier"]
            + " current "
            + context.sensor_type
    )
    assert patient_session_alerts_response["resources"][0]["valueText"] == context.priority, (
            "Expected priority "
            + patient_session_alerts_response["resources"][0]["valueText"]
            + " current "
            + context.priority
    )