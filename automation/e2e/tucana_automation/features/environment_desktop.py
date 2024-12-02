import csv
import json
import logging
import os
import platform

from os.path import exists

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager

from features.pages.web_utils import retry
from utils.slack_integration import send_slack_notification


def before_all(context):
    """before_all behave hook for DESKTOP browsers"""
    context.default_browser = "chrome"
    get_chrome_driver(context)
    context.options = webdriver.ChromeOptions()
    context.capabilities = DesiredCapabilities.CHROME
    if context.config.userdata.get("headless_browser", None):
        run_chrome_headless_mode(context)

    capture_network_event_logs(context)
    context.all_endpoint_calls = []


def before_feature(context, feature):
    """before_feature behave hook for DESKTOP browsers"""
    pass


def before_scenario(context, scenario):
    """before_scenario behave hook for DESKTOP browsers"""
    pass


def before_step(context, step):
    """before_step behave hook for DESKTOP browsers"""
    pass


def after_step(context, step):
    """after_step behave hook for DESKTOP browsers"""
    if "browser" in context:
        context.performance_logs[step.name] = context.browser.driver.get_log(
            "performance"
        )


def after_scenario(context, scenario):
    """after_scenario behave hook for DESKTOP browsers"""
    endpoint_calls = dump_network_event_api_logs(
        context.app_url, context.evidence_path, context.performance_logs, scenario.name
    )
    if endpoint_calls:
        context.all_endpoint_calls.extend(endpoint_calls)


def after_feature(context, feature):
    """after_feature behave hook for DESKTOP browsers"""
    pass


def after_all(context):
    """after_all behave hook for DESKTOP browsers"""
    if (
        context.env_config["always_notify_slack"]
        and context.env_config["slack_webhook"]
    ):
        send_slack_message(context)


# ####################################################################################################
# ########################################## HELPER METHODS ##########################################
# ####################################################################################################


def run_chrome_headless_mode(context):
    context.browser_args = {}
    context.options.add_argument("--headless")
    context.options.add_argument("--no-sandbox")
    context.options.add_argument("--window-size=1920,1080")
    context.options.add_argument("--disable-gpu")
    context.options.add_argument("--disable-dev-shm-usage")
    context.browser_args["options"] = context.options


@retry(4, 1)
def get_chrome_driver(context):
    platforms = {
        "Linux": "Running on Linux ... ",
        "Windows": "Running on Windows ... ",
        "Darwin": "Running on MAC ... ",
    }
    logging.info(platforms[platform.system()])
    context.chrome_orig_path = ChromeDriverManager().install()
    os.environ["PATH"] += os.pathsep + os.path.dirname(context.chrome_orig_path)


def capture_network_event_logs(context):
    context.capabilities["goog:loggingPrefs"] = {"performance": "ALL"}


def dump_network_event_api_logs(app_url, evidence_path, network_logs, scenario_name):
    try:
        api_list = [app_url + "/"]
        perf_log_apis = parse_network_event_logs(network_logs)
        all_output_dicts = []
        error_output_dicts = []
        for request_id in perf_log_apis:
            if "request_url" in perf_log_apis[request_id]:
                request_url = perf_log_apis[request_id]["request_url"]
                if any(api in request_url for api in api_list):
                    current_step = perf_log_apis[request_id]["step_name"]
                    request_url = perf_log_apis[request_id]["request_url"]
                    request_method = perf_log_apis[request_id]["request_method"]
                    total_time = "Unknown"
                    request_time = "Unknown"
                    response_time = "Unknown"
                    if (
                        "request_timestamp" in perf_log_apis[request_id]
                        and "response_timestamp" in perf_log_apis[request_id]
                    ):
                        request_time = (
                            float(perf_log_apis[request_id]["request_timestamp"]) / 1000
                        )
                        response_time = (
                            float(perf_log_apis[request_id]["response_timestamp"])
                            / 1000
                        )
                        total_time = round(response_time - request_time, 3)
                    response_status = (
                        perf_log_apis[request_id]["response_status"]
                        if "response_status" in perf_log_apis[request_id]
                        else "Unknown"
                    )
                    request_information = {
                        "scenario": scenario_name,
                        "step": current_step,
                        "endpoint": request_url,
                        "request_type": request_method,
                        "response_status": response_status,
                        "duration_secs": total_time,
                        "request_timestamp": request_time,
                        "response_timestamp": response_time,
                    }
                    all_output_dicts.append(request_information)
                    if str(response_status).startswith(("4", "5")):
                        error_output_dicts.append(request_information)

        perf_log_filename = os.path.join(evidence_path, "http_requests.csv")

        if len(all_output_dicts) > 0 or len(error_output_dicts) > 0:
            with open(
                perf_log_filename, "w", encoding="utf8", newline=""
            ) as output_file:
                dict_writer = csv.DictWriter(
                    output_file, fieldnames=all_output_dicts[0].keys()
                )
                dict_writer.writeheader()
                dict_writer.writerows(all_output_dicts)
            if error_output_dicts:
                # Writing file at scenario level
                failing_requests_filename = os.path.join(
                    evidence_path, "failing_http_requests.csv"
                )
                with open(
                    failing_requests_filename, "w", encoding="utf8", newline=""
                ) as output_file:
                    dict_writer = csv.DictWriter(
                        output_file, fieldnames=error_output_dicts[0].keys()
                    )
                    dict_writer.writeheader()
                    dict_writer.writerows(error_output_dicts)
                # Writing file at execution level
                failing_requests_filename = os.path.join(
                    os.environ.get("OUTPUT"), "failing_http_requests.csv"
                )
                if not exists(failing_requests_filename):
                    with open(
                        failing_requests_filename, "w", encoding="utf8", newline=""
                    ) as output_file:
                        dict_writer = csv.DictWriter(
                            output_file, fieldnames=error_output_dicts[0].keys()
                        )
                        dict_writer.writeheader()
                with open(
                    failing_requests_filename, "a", encoding="utf8", newline=""
                ) as output_file:
                    dict_writer = csv.DictWriter(
                        output_file, fieldnames=error_output_dicts[0].keys()
                    )
                    dict_writer.writerows(error_output_dicts)
            return all_output_dicts
    except Exception as ex:
        print(
            "Issue in 'after_scenario' when trying to store the network event logs:\n{}".format(
                ex
            )
        )


def parse_network_event_logs(network_logs):
    perf_log_apis = {}
    for key in network_logs:
        for log in network_logs[key]:
            message = json.loads(log["message"])["message"]
            method = json.loads(log["message"])["message"]["method"]
            if "requestId" in message["params"]:
                request_id = message["params"]["requestId"]
                if request_id not in perf_log_apis:
                    perf_log_apis[request_id] = {}
                if method == "Network.requestWillBeSent":
                    perf_log_apis[request_id]["request_url"] = message["params"][
                        "request"
                    ]["url"]
                    perf_log_apis[request_id]["request_timestamp"] = log["timestamp"]
                    perf_log_apis[request_id]["request_method"] = message["params"][
                        "request"
                    ]["method"]
                    perf_log_apis[request_id]["step_name"] = key
                elif method == "Network.responseReceived":
                    perf_log_apis[request_id]["response_status"] = message["params"][
                        "response"
                    ]["status"]
                elif method in ["Network.loadingFinished", "Network.loadingFailed"]:
                    perf_log_apis[request_id]["response_timestamp"] = log["timestamp"]
    return perf_log_apis


def send_slack_message(context):
    slack_webhook = context.env_config["slack_webhook"]
    environment = context.config.userdata.get("env")

    app_version = ""

    company = context.env_config["company"]
    app_name = context.env_config["app_name"]
    report_url = "https://github.com/sibelhealth/tucana/actions/runs/" + os.environ.get(
        "GITHUB_RUN_ID", ""
    )

    company_notification = ""
    if company:
        company_notification = "\nAPP: *{}* - *{}*".format(company, app_name)

    print("Execution summary filename: {}".format(context.execution_summary_filename))

    muted_scenarios, executed_scenarios, failing_scenarios = process_scenarios(context)

    if failing_scenarios:
        scenarios_text = ""
        if len(failing_scenarios) > 10:
            scenarios_text += (
                "You have more than 10 failed Scenarios, Please open the test report..."
            )
        else:
            for scenario in failing_scenarios:
                scenarios_text += "\n```• {}```".format(scenario)
        slack_data = {
            "username": "Automation",
            "icon_emoji": ":rocket:",
            "channel": "#automation-notifications",
            "attachments": [
                {
                    "title": ":rotating_light: {} - FAILED!".format(
                        "TUCANA QA TEST EXECUTION"
                    ),
                    "text": "*Scenarios*\nExecuted: *{}*\nMuted (impacted by bugs): *{}*\nFailed: *{}* {}".format(
                        executed_scenarios,
                        muted_scenarios,
                        len(failing_scenarios),
                        company_notification,
                    ),
                    "color": "#CC3333",
                    "fields": [
                        {
                            "title": "Environment:",
                            "value": environment,
                            "short": "false",
                        },
                        {
                            "title": "APP Version:",
                            "value": app_version,
                            "short": "true",
                        },
                        {"title": "Report URL:", "value": report_url, "short": "false"},
                    ],
                },
                {
                    "title": "Failing Scenarios:",
                    "color": "#CC3333",
                    "text": scenarios_text,
                },
            ],
        }
    else:
        slack_data = {
            "username": "Automation",
            "icon_emoji": ":rocket:",
            "channel": "#automation-notifications",
            "attachments": [
                {
                    "title": ":tada: {} - SUCCEEDED!".format(
                        "TUCANA QA TEST EXECUTION"
                    ),
                    "text": "*Scenarios*\nExecuted: *{}* \nMuted (impacted by bugs): *{}* {}".format(
                        executed_scenarios, muted_scenarios, company_notification
                    ),
                    "color": "#33CC33",
                    "fields": [
                        {
                            "title": "Environment:",
                            "value": environment,
                            "short": "false",
                        },
                        {
                            "title": "APP Version:",
                            "value": app_version,
                            "short": "true",
                        },
                        {"title": "Report URL:", "value": report_url, "short": "false"},
                    ],
                }
            ],
        }
    send_slack_notification(slack_webhook, slack_data)


def process_scenarios(context):
    muted_scenarios = 0
    executed_scenarios = 0
    failing_scenarios = []
    try:
        with open(context.execution_summary_filename, "r") as f:
            all_scenarios = f.readlines()
            for scenario_line in all_scenarios:
                if "MUTED_SCENARIO" in scenario_line:
                    muted_scenarios += 1
                if "EXECUTED_SCENARIO" in scenario_line:
                    executed_scenarios += 1
                if "FAILING_SCENARIO" in scenario_line:
                    failing_scenarios.append(
                        scenario_line.replace("FAILING_SCENARIO: ", "").replace(
                            "$", "\n "
                        )
                    )
    except Exception:
        raise Exception("Couldn't open the execution summary file")

    return muted_scenarios, executed_scenarios, failing_scenarios
