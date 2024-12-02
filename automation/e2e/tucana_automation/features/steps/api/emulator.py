import json
import logging
import time
import uuid

from behave import step
from faker import Faker

from features.steps.api.common_api_steps import verify_request_status
from features.steps.api.device_steps import assign_pm_bed
from features.steps.common import parse_text, assert_response
from features.steps.factories import (
    CreateOrUpdateDeviceFactory,
    ConnectPatientMonitorFactory,
    OpenPatientSessionFactory,
    ConnectSensorFactory,
    UpdateSensorModeFactory,
)
from utils.api_utils import requests_post, requests_get, set_alarm_to_patient

technical_alerts_and_alarms_codes = {
    "SENSOR_OUT_OF_RANGE": "258098",
    "LOW_SIGNAL": "258118",
    "CRITICAL_SENSOR_BATTERY": "258106",
    "LOW_SENSOR_BATTERY": "258102",
    "LEAD_OFF": "258110",
    "POOR_SKIN_CONTACT": "258146",
    "LOOSE_SLEEVE": "258142",
    "WEAK_PULSE": "258150",
    "MOVEMENT_DETECTED": "258134",
    "FINGER_NOT_DETECTED": "258122",
    "SENSOR_FAILURE": "258138",
    "SENSOR_ERROR": "258126",
    "SYSTEM_ERROR": "258130",
    "MODULE_FAILURE": "258114"
}

physiological_audio_alert_alarms_codes = {
    "HR_Low_AUDIO": '258053',
    "HR_High_AUDIO": '258049',
    "RR_Low_AUDIO": '258057',
    "RR_High_AUDIO": '258061',
    "SPO2_Low_AUDIO": '258065',
    "SPO2_High_AUDIO": '258069',
    "PR_Low_AUDIO": '258177',
    "PR_High_AUDIO": '258181',
    "NIBP_SYS_Low_AUDIO": '258073',
    "NIBP_SYS_High_AUDIO": '258077',
    "NIBP_DIA_Low_AUDIO": '258081',
    "NIBP_DIA_High_AUDIO": '258085',
    "BODY_Temp_Low_AUDIO": '258161',
    "BODY_Temp_High_AUDIO": '258165',
    "CHEST_Skin_Temp_Low_AUDIO": '258153',
    "CHEST_Skin_Temp_High_AUDIO": '258157',
    "LIMB_Skin_Temp_Low_AUDIO": '258153',
    "LIMB_Skin_Temp_High_AUDIO": '258157',
    "FALL_AUDIO": '258169',
    "POSITION_AUDIO": '258173',
}

physiological_alerts_and_alarms_codes = {
    "HR_Low_VISUAL": '258054',
    "HR_High_VISUAL": '258050',
    "RR_Low_VISUAL": '258058',
    "RR_High_VISUAL": '258062',
    "SPO2_Low_VISUAL": '258066',
    "SPO2_High_VISUAL": '258070',
    "PR_Low_VISUAL": '258178',
    "PR_High_VISUAL": '258182',
    "NIBP_SYS_Low_VISUAL": '258074',
    "NIBP_SYS_High_VISUAL": '258078',
    "NIBP_DIA_Low_VISUAL": '258082',
    "NIBP_DIA_High_VISUAL": '258086',
    "BODY_Temp_Low_VISUAL": '258162',
    "BODY_Temp_High_VISUAL": '258166',
    "CHEST_Skin_Temp_Low_VISUAL": '258154',
    "CHEST_Skin_Temp_High_VISUAL": '258158',
    "LIMB_Skin_Temp_Low_VISUAL": '258154',
    "LIMB_Skin_Temp_High_VISUAL": '258158',
    "FALL_VISUAL": '258170',
    "POSITION_VISUAL": '258174'
}

sensors = {
    "ANNE Chest": {
        "Physiological": ["HR_Low", "HR_High", "RR_Low", "RR_High", "CHEST_Skin_Temp_Low", "CHEST_Skin_Temp_High",
                          "FALL",
                          "POSITION"], "Technical": ["SENSOR_OUT_OF_RANGE", "LEAD_OFF", "MODULE_FAILURE"]},
    "Nonin 3150": {
        "Physiological": ["SPO2_Low", "SPO2_High", "NIBP_SYS_Low", "NIBP_SYS_High", "NIBP_DIA_Low", "NIBP_DIA_High",
                          "PR_Low", "PR_High"],
        "Technical": ["SENSOR_OUT_OF_RANGE", "FINGER_NOT_DETECTED", "SENSOR_ERROR", "SYSTEM_ERROR"]},
    "DMT Thermometer": {"Physiological": ["BODY_Temp_Low", "BODY_Temp_High"]},
    "Viatom BP monitor": {"Physiological": ["NIBP_SYS_Low", "NIBP_SYS_High", "NIBP_DIA_Low", "NIBP_DIA_High"],
                          "Technical": ["LOOSE_SLEEVE", "WEAK_PULSE", "MOVEMENT_DETECTED", "SENSOR_FAILURE"]},
    "ANNE Limb": {
        "Physiological": ["LIMB_Skin_Temp_Low", "LIMB_Skin_Temp_High", "SPO2_Low", "SPO2_High", "PR_Low", "PR_High"],
        "Technical": ["POOR_SKIN_CONTACT", "MODULE_FAILURE", "SENSOR_OUT_OF_RANGE"]}
}

alarms_type_list = {
    "physiological": [
        "HR_Low_VISUAL",
        "HR_High_VISUAL",
        "RR_Low_VISUAL",
        "RR_High_VISUAL",
        "SPO2_Low_VISUAL",
        "SPO2_High_VISUAL",
        "PR_Low_VISUAL",
        "PR_High_VISUAL",
        "NIBP_SYS_Low_VISUAL",
        "NIBP_SYS_High_VISUAL",
        "NIBP_DIA_Low_VISUAL",
        "NIBP_DIA_High_VISUAL",
        "BODY_Temp_Low_VISUAL",
        "BODY_Temp_High_VISUAL",
        "CHEST_Skin_Temp_Low_VISUAL",
        "CHEST_Skin_Temp_High_VISUAL"
        "LIMB_Skin_Temp_Low_VISUAL",
        "LIMB_Skin_Temp_High_VISUAL",
        "FALL_VISUAL",
        "POSITION_VISUAL"
    ]
}


@step('Tom creates a Patient Monitor "{}"')
@step('Tom creates a Patient Monitor "{}" with the following data')
def create_patient_monitor(context, primary_identifier):
    data = parse_text(context)
    data = CreateOrUpdateDeviceFactory.build(
        **data, primary_identifier=primary_identifier, device_code="Patient Monitor"
    )
    response = context.api_client.put(
        "/web/device", json=json.loads(data.model_dump_json())
    )

    context.response = response
    assert_response(response, f"CreateDevice (PM: {primary_identifier})")
    context.emulator_registry[primary_identifier] = {
        "PatientMonitor": data.model_dump(),
        "Sensors": [],
        "Session": {},
    }
    context.device_uuid = str(data.id)
    logging.info(f'Created PM device with id {context.device_uuid}')
    context.pm_name_ids[primary_identifier] = context.device_uuid


@step('Tom connects the Patient Monitor "{}"')
def connect_patient_monitor(context, primary_identifier):
    data = ConnectPatientMonitorFactory.build(primary_identifier=primary_identifier)
    response = context.emulator_client.post(
        "/monitor/ConnectPatientMonitor", json=json.loads(data.model_dump_json())
    )
    assert_response(response, f"ConnectPatientMonitor (PM: {primary_identifier})")


@step("Tom connects all Patient Monitors")
def connect_all_patient_monitors(context):
    for primary_identifier in context.emulator_registry.keys():
        data = {"primary_identifier": primary_identifier}
        response = context.emulator_client.post(
            "/monitor/ConnectPatientMonitor", json=data
        )
        assert_response(response, f"ConnectPatientMonitor (PM: {primary_identifier})")


@step("Tom disconnects all Patient Monitors")
def disconnect_all_patient_monitors(context):
    for primary_identifier in context.emulator_registry.keys():
        data = {"primary_identifier": primary_identifier}
        response = context.emulator_client.post(
            "/monitor/DisconnectPatientMonitor", json=data
        )
        assert_response(
            response, f"DisconnectPatientMonitor (PM: {primary_identifier})"
        )


@step("{} ANNE Chest sensors are connected to the Patient Monitors")
def connect_sensor_with_data(context, sensor_qty):
    faker = Faker()
    pm_names = list(context.pm_name_ids.keys())
    context.pm_names_sensor_id = {}
    for i in range(int(sensor_qty)):
        time.sleep(1)
        sensor_id = faker.bothify("SMUL-QA-##-###")
        data = {
            "device_code": "ANNE Chest",
            "primary_identifier": sensor_id,
            "name": "ANNE Chest"
        }
        data = ConnectSensorFactory.build(**data, patient_monitor_primary_identifier=pm_names[i])
        response = context.emulator_client.post("/sensor/ConnectSensor", json=json.loads(data.model_dump_json()))
        context.response = response
        assert_response(response, f"ConnectSensor (PM: {pm_names[i]})")
        context.pm_names_sensor_id[sensor_id] = pm_names[i]

        if "Sensors" in context.emulator_registry[pm_names[i]]:
            context.emulator_registry[pm_names[i]]["Sensors"].append(
                data.model_dump()
            )
        else:
            context.emulator_registry[pm_names[i]]["Sensors"] = [data.model_dump()]

        context.sensors_id.append(data.primary_identifier)
        context.sensor_id = data.primary_identifier


@step('Tom connects a sensor to the Patient Monitor "{}"')
@step('Tom connects a sensor to the Patient Monitor "{}" with the following data')
def connect_sensor(context, primary_identifier):
    data = parse_text(context)
    data = ConnectSensorFactory.build(**data, patient_monitor_primary_identifier=primary_identifier)

    response = context.emulator_client.post(
        "/sensor/ConnectSensor", json=json.loads(data.model_dump_json())
    )
    context.response = response

    assert_response(response, f"ConnectSensor (PM: {primary_identifier})")

    if "Sensors" in context.emulator_registry[primary_identifier]:
        context.emulator_registry[primary_identifier]["Sensors"].append(
            data.model_dump()
        )
    else:
        context.emulator_registry[primary_identifier]["Sensors"] = [data.model_dump()]

    context.sensors_id.append(data.primary_identifier)
    context.sensor_id = data.primary_identifier
    context.device_code = data.device_code


@step('Tom disconnects the sensor "{}"')
def disconnect_sensor(context, primary_identifier):
    data = {"primary_identifier": primary_identifier}
    response = context.emulator_client.post("/sensor/DisconnectSensor", json=data)
    context.response = response
    assert_response(response, "DisconnectSensor")
    if len(context.sensors_id) > 0:
        context.sensors_id.remove(primary_identifier)


@step('Tom updates the mode of the sensor "{}"')
@step('Tom updates the mode of the sensor "{}" with the following data')
def update_sensor_mode(context, primary_identifier):
    data = parse_text(context)
    data = UpdateSensorModeFactory.build(
        **data, primary_identifier=primary_identifier
    ).model_dump_json()

    response = context.emulator_client.post("/sensor/UpdateSensorMode", data=data)
    context.response = response

    assert_response(response, "UpdateSensorMode")


@step('Tom disconnects the Patient Monitor "{}"')
def disconnect_patient_monitor(context, primary_identifier):
    data = {"primary_identifier": primary_identifier}

    response = context.emulator_client.post("/monitor/DisconnectMonitor", json=data)
    context.response = response
    assert_response(response, "DisconnectPatientMonitor")


@step('Tom opens a session for the Patient Monitor "{}"')
@step('Tom opens a session for the Patient Monitor "{}" with the following data')
def open_patient_session(context, primary_identifier):
    data = parse_text(context)
    data = OpenPatientSessionFactory.build(**data,
                                           patient_monitor_primary_identifier=primary_identifier).model_dump_json()
    response = context.emulator_client.post("/monitor/OpenPatientSession", data=data)
    context.response = response
    assert_response(response, "OpenPatientSession")
    context.emulator_registry[primary_identifier] = {"Session": json.loads(data)}


@step('Tom closes a session for the Patient Monitor "{}"')
@step('Tom closes a session for the Patient Monitor "{}" with the following data')
def close_patient_session(context, primary_identifier):
    data = {"patient_monitor_primary_identifier": primary_identifier}

    response = context.emulator_client.post("/monitor/ClosePatientSession", json=data)

    context.response = response
    assert_response(response, "ClosePatientSession")
    context.emulator_registry[primary_identifier] = {"Session": {}}


@step('Tom deletes a Patient Monitor "{}"')
def delete_patient_monitor(context, primary_identifier):
    data = {"device_id": context.device_uuid}

    response = context.emulator_client.post(
        "/proxy/device/command/DeleteDevice", json=data
    )

    context.response = response

    assert_response(response, "DeleteDevice")
    context.pm_name_ids.pop(primary_identifier)


@step("{} Patient exists with the following data")
def create_patient_for_emulators(context, patient_qty):
    faker = Faker()
    if int(patient_qty) != 1:
        context.patient_id = str(uuid.uuid1())
        context.primary_identifier = faker.unique.bothify("PMUL-QA-##-#####")
        context.patient_gender = faker.random_elements(elements=("female", "male"), length=1)
        if context.patient_gender[0] == "male":
            context.patient_given_name = faker.first_name_male()
        else:
            context.patient_given_name = faker.first_name_female()

        context.patient_family_name = faker.last_name()
        context.active = True
        context.birth_date = faker.date()
        context.patient_emulator_data = {
            "patient":
                {
                    "id": context.patient_id,
                    "given_name": context.patient_given_name,
                    "family_name": context.patient_family_name,
                    "gender": context.patient_gender[0],
                    "active": context.active,
                    "primary_identifier": context.primary_identifier,
                    "birthDate": context.birth_date,
                }
        }
        context.patients_ids.append(context.patient_id)
    else:
        context.patient_emulator_data = parse_text(context)

    response = requests_post(context, '/web/patient', context.patient_emulator_data['patient'], headers=None)
    assert_response(response, "Create Emulator Patient", 200)

    if int(patient_qty) == 1:
        context.patient_bed_and_group["patient"] = context.patient_emulator_data['patient']['id']

    context.patient_primary_id = context.patient_emulator_data['patient']['primary_identifier']
    clean_data = context.patient_emulator_data
    clean_data['patient']['birth_date'] = clean_data['patient']['birthDate']
    del clean_data['patient']['birthDate']
    del clean_data['patient']['active']
    del clean_data['patient']['id']
    context.patient_emulator_data = clean_data
    if int(patient_qty) != 1:
        context.multiple_patient_emulator_data.append(context.patient_emulator_data)


@step('Tom connects the Patient Monitor "{}" to the existent patient')
@step(
    'Tom connects the Patient Monitor "{}" to the existent patient with "{config_option}" config option {config_value}')
def connects_pm_existent_patient(context, primary_identifier, config_option='audio_enabled', config_value='False'):
    config = {'audio_pause_enabled': False, 'audio_enabled': False}
    config[config_option] = json.loads(config_value.lower())
    data = ConnectPatientMonitorFactory.build(**context.patient_emulator_data, primary_identifier=primary_identifier,
                                              name=primary_identifier + "-LN", connected_sensors=[],
                                              config=config).model_dump_json()
    response = context.emulator_client.post("/monitor/ConnectPatientMonitor", data=data)
    assert_response(response, f"ConnectPatientMonitor (PM: {primary_identifier})")


@step("{} Patient Monitor exists")
def multiple_patient_monitors(context, quantity):
    faker = Faker()
    for i in range(int(quantity)):
        context.patient_monitor_primary_identifier = faker.unique.bothify("MPM-###-#####")
        create_patient_monitor(context, context.patient_monitor_primary_identifier)


@step("{} Patient Monitors are connected to the existent patients")
def connect_multiple_pm_and_patients(context, patient_monitors_qty):
    pm_names = list(context.pm_name_ids.keys())
    context.patient_ed_pm_name = {}
    for i in range(int(patient_monitors_qty)):
        context.patient_emulator_data = context.multiple_patient_emulator_data[i]
        time.sleep(2)
        context.patient_ed_pm_name[pm_names[i]] = context.patient_emulator_data
        connects_pm_existent_patient(context, pm_names[i])


@step("{} Patient Monitors are assigned to the beds")
def multiple_pm_to_multiple_beds(context, pm_quantity):
    pm_names = list(context.pm_name_ids.keys())
    context.pm_to_beds = {}
    for i in range(int(pm_quantity)):
        context.bed_id = context.bed_ids[i]
        context.device_uuid = context.pm_name_ids[pm_names[i]]
        context.pm_to_beds[context.bed_id] = context.device_uuid
        assign_pm_bed(context)


@step("{} Patients exists")
def multiple_patients(context, quantity):
    context.patients_ids = []
    for i in range(int(quantity)):
        create_patient_for_emulators(context, quantity)


@step("Tom verifies the current PM quantity")
def current_pm_quantity(context):
    url = "/web/device"
    context.response = requests_get(context, url, headers=None)
    assert context.response.status_code == 200, f"Expected status code 200, current {context.response.status_code}"
    jsonify_response = json.loads(context.response.text)
    pm_qty = 0
    for resource in jsonify_response['resources']:
        if resource['device_code'] == 'Patient Monitor':
            pm_qty += 1
    context.current_pm_qty = pm_qty


@step("Tom creates all the remaining PMs to complete the limit system of {} PM")
def create_remaining_pm(context, limit):
    faker = Faker()
    for i in range(int(limit) - context.current_pm_qty):
        create_patient_monitor(context, faker.bothify("PM-QTY-AU-000") + str(context.current_pm_qty + (i + 1)))


@step("Tom creates one extra Patient Monitor and expects not to see it inside the list")
def create_extra_pm(context):
    context.pm_extra = "PM-QTY-AU-EXTRA-65"
    create_patient_monitor(context, context.pm_extra)


@step('Tom "{}" a "{}" alarm for the sensor "{}" with the code "{}" with priority "{}"')
def trigger_alarm(context, trigger, alarm_type, sensor_type, alarm_code, priority):
    if trigger == "activate":
        active = True
    else:
        active = False
    context.alarm_code = alarm_code
    context.sensor_type = sensor_type
    context.alarm_type = alarm_type
    context.priority = priority
    context.response = set_alarm_to_patient(context, context.patient_primary_id, context.alarm_code, context.priority,
                                            active, context.device_code, context.sensor_type)
    verify_request_status(context, 204, "No Content")


@step('The device is removed to keep the application clean')
def delete_device(context):
    data = {"device_id": context.device_uuid}
    response = context.emulator_client.post(
        "/proxy/device/command/DeleteDevice", json=data
    )
    context.response = response
    assert_response(response, "DeleteDevice")
