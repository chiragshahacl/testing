import json
import os
import sys
from pathlib import Path

from behavex_web.steps.web import *
from httpx import Client

# noinspection PyUnresolvedReferences
from features import env_manager
from features.steps.api.bed_groups_steps import remove_bed_group_clean_application
from features.steps.api.bed_steps import remove_all_beds_clean_application
from features.steps.api.common_api_steps import deletes_all_data
from features.steps.api.patient_steps import remove_patients_clean_application
from features.steps.common import init_api_client, init_emulator_client, assert_response
from features.steps.web.alarms_step import clean_activated_alarms
from utils.beds_pm_in_hooks import clean_all_through_api, create_bed_and_pm_through_api, assign_bed_to_pm


def before_all(context):
    """before_all behave hook"""
    load_users_information(context)
    always_notify_slack_string = context.config.userdata.get(
        "always_notify_slack", "false"
    ).lower()
    always_notify_slack = True if always_notify_slack_string == "true" else False

    if (os.environ.get("WEB_APP_USER") and os.environ.get("WEB_APP_PASS")) is None:
        print(
            "WEB_APP_USER, WEB_APP_PASS environment variables are needed please fix it before continue"
        )
        sys.exit(1)

    if context.config.userdata.get("env") is None:
        environment = "dev"
    else:
        environment = context.config.userdata.get("env").lower()

    for env in context.config_data["tucana_envs"]:
        if env["environment"] == environment:
            context.app_url = env["url"]
            context.api_url = env["api"]
    logging.info(
        "Sibel Health - {} APP - API URL: {}".format("Tucana", context.api_url)
    )

    # Storing all variables in a context variable
    context.env_config = {
        "app_url": context.app_url,
        "api_url": context.api_url,
        "app_name": "Tucana",
        "environment": environment.upper(),
        "execution_tags": os.environ.get("TAGS", "").upper().split(";"),
        "slack_webhook": os.environ.get("SLACK_WEBHOOK_SECRET", None),
        "always_notify_slack": always_notify_slack,
        "username": os.environ.get("WEB_APP_USER", None),
        "password": os.environ.get("WEB_APP_PASS", None),
        "company": "Sibel Health",
    }
    context.execution_summary_filename = os.path.abspath(
        os.path.join(os.environ.get("OUTPUT"), "..", "output", "execution_summary.txt")
    )
    if environment.upper() == "PROD":
        if os.environ.get("WEB_APP_PROD_PASS") is None:
            print(
                "WEB_APP_PROD_PASS environment variable is needed, please fix it before continue"
            )
            sys.exit(1)
        context.env_config["password"] = os.environ.get("WEB_APP_PROD_PASS", None)

    # Stores the data used on the PatientMonitor emulator to be referenced in all steps
    context.emulator_registry = {}

    # Stores Bed ids to keep it clean
    context.bed_ids = []
    context.bed_hook_ids = []

    # Stores PM ids to keep it clean
    context.pm_name_ids = {}
    context.pm_hook_ids = {}

    # Stores Scenarios data to keep it clean
    context.patient_bed_and_group = {}

    # Stores sensors to keep it clean
    context.sensors_id = []

    # Stores multiple beds activated alarms
    context.multiple_activated_alarms = []
    context.multiple_patient_emulator_data = []

    # Create a new bed through api to assure tests stability
    create_bed_and_pm_through_api(context)

    # Assign bed to pm
    assign_bed_to_pm(context)

    # Create a new bed through api to assure tests stability
    create_bed_and_pm_through_api(context)


def before_feature(context, features):
    """before_feature behave hook"""
    for feature in features.scenarios:
        if "DEPRECATED" in feature.tags:
            feature.skip("This feature has been deprecated...")
        else:
            for tag in feature.tags:
                if "MUTE_" in tag:
                    feature.tags.append("MUTE")
                    break


def before_scenario(context, scenario):
    """before_scenario behave hook"""
    context.record_network_event_api_logs = True
    context.performance_logs = {}
    if "MUTE" in scenario.tags and "MUTE" not in context.env_config["execution_tags"]:
        scenario.skip(
            "Avoid running muted scenario (it will be run in a separate test plan)"
        )
        return

    context.performance_scenario = True if "PERFORMANCE" in scenario.tags else False

    # Requests session for emulator and web requests
    init_emulator_client(context)
    init_api_client(context)

    print("------------------------------------------")
    print("Running Scenario: {}".format(scenario.name))
    print("------------------------------------------")


def before_step(context, step):
    """before_step behave hook"""
    context.step = step


def after_step(context, step):
    """after_step behave hook"""
    pass


def after_scenario(context, scenario):
    """after_scenario behave hook"""
    with open(context.execution_summary_filename, "a+") as f:
        if "MUTE" in scenario.tags and scenario.status == "failed":
            f.write(
                "MUTED_SCENARIO: {}: {}\n".format(scenario.feature.name, scenario.name)
            )
        if "MUTE" not in scenario.tags and scenario.status == "failed":
            failed_cause = ""
            for step_detail in scenario.steps:
                if step_detail.exception is not None:
                    failed_cause = step_detail.exception
            f.write(
                "FAILING_SCENARIO: {}${}$ERROR: {}\n".format(
                    scenario.feature.name, scenario.name, failed_cause
                )
            )
        if scenario.status in ["passed", "failed"]:
            f.write(
                "EXECUTED_SCENARIO: {}: {}\n".format(
                    scenario.feature.name, scenario.name
                )
            )
            print("------------------------------------------")
            print("Scenario Completed: {}".format(scenario.name))
            print("------------------------------------------")

    # Clean pm just in case of failed steps
    clean_all_pm_and_sensors(context)

    # Clean Patient, Bed and group in case of failure
    clean_all_patient_data(context)

    # Clean Alarms
    clean_activated_alarms(context)


def after_feature(context, feature):
    """after_feature behave hook"""
    pass


def after_all(context):
    """after_all behave hook"""
    # Clean the bed and PM created through API
    clean_all_through_api(context)


# ####################################################################################################
# ########################################## HELPER METHODS ##########################################
# ####################################################################################################
# noinspection PyBroadException
def load_users_information(context):
    try:
        config_path = Path.cwd() / "config.json"
        with open(str(config_path)) as json_file:
            config_data = json.load(json_file)
        context.config_data = config_data
    except Exception:
        print("Please Contact Admin and ask for the config file")
        sys.exit(1)


def clean_all_pm_and_sensors(context):
    if len(context.sensors_id) > 0:
        for primary_identifier in context.sensors_id.copy():
            try:
                data = {"primary_identifier": primary_identifier}
                response = context.emulator_client.post("/sensor/DisconnectSensor", json=data)
                context.response = response
                assert_response(response, "DisconnectSensor")
                logging.info(f'Sensor {primary_identifier} disconnected')
                context.sensors_id.remove(primary_identifier)
            except AssertionError:
                pass

    if len(context.pm_name_ids) > 0:
        for pm in context.pm_name_ids.copy():
            context.emulator_client = Client(base_url=context.env_config["api_url"] + "/emulator")
            try:
                data = {"primary_identifier": pm}
                response = context.emulator_client.post("/monitor/DisconnectMonitor", json=data)
                context.response = response
                assert_response(response, "DisconnectMonitor")
            except AssertionError:
                pass

            logging.info(f"Deleting Patient Monitor: {pm} - {context.pm_name_ids[pm]}")
            data = {"device_id": context.pm_name_ids[pm]}

            response = context.emulator_client.post(
                "/proxy/device/command/DeleteDevice", json=data
            )
            assert_response(response, "DeleteDevice")
            context.pm_name_ids.pop(pm)


# noinspection DuplicatedCode
def clean_all_patient_data(context):
    if "bed_ids" in context:
        if len(context.bed_ids) > 0:
            remove_all_beds_clean_application(context)

    if "patients_ids" in context:
        if len(context.patients_ids) > 0:
            remove_patients_clean_application(context)

    if "bed_group_id" in context:
        if context.bed_group_id is not None:
            remove_bed_group_clean_application(context)

    deletes_all_data(context)


