from datetime import timedelta

from behave import given, then, when
from test_tools.asserts import assert_deep_equal

from features.factories.physiological_alert_factory import PhysiologicalAlertFactory


@given("There are {size:d} paired physiological alerts to the patient")
def add_paired_physiological_alerts(context, size):
    if not hasattr(context, "patient"):
        raise ValueError("A patient needs to be created before running this step")

    context.expected_response = []
    for _ in range(size):
        active_alert = PhysiologicalAlertFactory(active=True, patient_id=context.patient.id)
        inactive_alert = PhysiologicalAlertFactory(
            patient_id=context.patient.id,
            code=active_alert.code,
            device_primary_identifier=active_alert.device_primary_identifier,
            determination_time=active_alert.determination_time + timedelta(hours=1),
            active=False,
        )
        context.db.add(active_alert)
        context.db.add(inactive_alert)
        context.db.commit()

        context.expected_response.append(
            {
                "code": active_alert.code,
                "start_determination_time": active_alert.determination_time.isoformat(),
                "end_determination_time": inactive_alert.determination_time.isoformat(),
                "value_text": active_alert.value_text,
                "device_primary_identifier": active_alert.device_primary_identifier,
                "device_code": active_alert.device_code,
                "trigger_lower_limit": None,
                "trigger_upper_limit": None,
            }
        )


@given("There are {size:d} only active physiological alerts to the patient")
def add_only_active_physiological_alerts(context, size):
    if not hasattr(context, "patient"):
        raise ValueError("A patient needs to be created before running this step")

    for _ in range(size):
        active_alert = PhysiologicalAlertFactory(active=True, patient_id=context.patient.id)
        context.db.add(active_alert)
        context.db.commit()

    context.expected_response = []


@given("There are {size:d} only inactive physiological alerts to the patient")
def add_only_inactive_physiological_alerts(context, size):
    if not hasattr(context, "patient"):
        raise ValueError("A patient needs to be created before running this step")

    for _ in range(size):
        inactive_alert = PhysiologicalAlertFactory(active=False, patient_id=context.patient.id)
        context.db.add(inactive_alert)
        context.db.commit()

    context.expected_response = []


@given("There are a mixed of paired and incomplete physiological alerts to the patient")
def add_mix_physiological_alerts(context):
    # add valid alerts and set the expectation
    add_paired_physiological_alerts(context, 5)

    for _ in range(5):  # adds only active
        inactive_alert = PhysiologicalAlertFactory(active=True, patient_id=context.patient.id)
        context.db.add(inactive_alert)
        context.db.commit()

    for _ in range(5):  # adds only inactive
        inactive_alert = PhysiologicalAlertFactory(active=False, patient_id=context.patient.id)
        context.db.add(inactive_alert)
        context.db.commit()


@given("There is an alert paired multiple times for the patient")
def add_same_physiological_alerts(context):
    context.expected_response = []

    active_alert = PhysiologicalAlertFactory(active=True, patient_id=context.patient.id)
    inactive_alert = PhysiologicalAlertFactory(
        patient_id=context.patient.id,
        code=active_alert.code,
        device_primary_identifier=active_alert.device_primary_identifier,
        determination_time=active_alert.determination_time + timedelta(seconds=1),
        active=False,
    )

    context.db.add(active_alert)
    context.db.add(inactive_alert)
    context.db.commit()

    context.expected_response.append(
        {
            "code": active_alert.code,
            "start_determination_time": active_alert.determination_time.isoformat(),
            "end_determination_time": inactive_alert.determination_time.isoformat(),
            "value_text": active_alert.value_text,
            "device_primary_identifier": active_alert.device_primary_identifier,
            "device_code": active_alert.device_code,
            "trigger_lower_limit": None,
            "trigger_upper_limit": None,
        }
    )

    active_alert = PhysiologicalAlertFactory(
        patient_id=context.patient.id,
        code=active_alert.code,
        device_primary_identifier=active_alert.device_primary_identifier,
        determination_time=active_alert.determination_time + timedelta(seconds=2),
        active=True,
    )
    inactive_alert = PhysiologicalAlertFactory(
        patient_id=context.patient.id,
        code=active_alert.code,
        device_primary_identifier=active_alert.device_primary_identifier,
        determination_time=active_alert.determination_time + timedelta(seconds=3),
        active=False,
    )

    context.db.add(active_alert)
    context.db.add(inactive_alert)
    context.db.commit()

    context.expected_response.append(
        {
            "code": active_alert.code,
            "start_determination_time": active_alert.determination_time.isoformat(),
            "end_determination_time": inactive_alert.determination_time.isoformat(),
            "value_text": active_alert.value_text,
            "device_primary_identifier": active_alert.device_primary_identifier,
            "device_code": active_alert.device_code,
            "trigger_lower_limit": None,
            "trigger_upper_limit": None,
        }
    )


@given("There is an alert paired but active multiple times")
def add_same_physiological_alerts_active_multiple_times(context):
    context.expected_response = []

    for i in range(5):
        active_alert = PhysiologicalAlertFactory(
            determination_time=context.now + timedelta(hours=i),
            active=True,
            patient_id=context.patient.id,
        )  # an active alert every hour
        context.db.add(active_alert)

    inactive_alert = PhysiologicalAlertFactory(
        patient_id=context.patient.id,
        code=active_alert.code,
        device_primary_identifier=active_alert.device_primary_identifier,
        determination_time=active_alert.determination_time + timedelta(seconds=1),
        active=False,
    )  # inactive after the last active

    context.db.add(inactive_alert)
    context.db.commit()

    context.expected_response.append(
        {
            "code": active_alert.code,
            # last active added (newer) is the expected for determination_time
            "start_determination_time": active_alert.determination_time.isoformat(),
            "end_determination_time": inactive_alert.determination_time.isoformat(),
            "value_text": active_alert.value_text,
            "device_primary_identifier": active_alert.device_primary_identifier,
            "device_code": active_alert.device_code,
            "trigger_lower_limit": None,
            "trigger_upper_limit": None,
        }
    )


@given("There is an alert paired but inactive multiple times")
def add_same_physiological_alerts_inactive_multiple_times(context):
    context.expected_response = []

    active_alert = PhysiologicalAlertFactory(
        active=True,
        patient_id=context.patient.id,
    )
    inactive_alerts = []

    for i in range(5):
        inactive_alert = PhysiologicalAlertFactory(
            patient_id=context.patient.id,
            code=active_alert.code,
            device_primary_identifier=active_alert.device_primary_identifier,
            determination_time=active_alert.determination_time + timedelta(hours=i + 1),
            active=False,
        )
        context.db.add(inactive_alert)
        inactive_alerts.append(inactive_alert)

    context.db.add(active_alert)
    context.db.commit()

    context.expected_response.append(
        {
            "code": active_alert.code,
            "start_determination_time": active_alert.determination_time.isoformat(),
            "end_determination_time": inactive_alerts[
                0
            ].determination_time.isoformat(),  # inactive alert used is the oldest one
            "value_text": active_alert.value_text,
            "device_primary_identifier": active_alert.device_primary_identifier,
            "device_code": active_alert.device_code,
            "trigger_lower_limit": None,
            "trigger_upper_limit": None,
        }
    )


@given("A request to get the physiological alerts of the patient")
def set_physiological_alerts_request(context):
    if not hasattr(context, "patient"):
        raise ValueError("A patient needs to be created before running this step")

    context.request = {"url": f"/patient/{context.patient.id}/session/alerts"}


@when("The request is made to get physiological alerts")
def get_physiological_alerts(context):
    context.response = context.client.get(**context.request)


@then("The expected physiological alert response is returned")
def check_physiological_response(context):
    assert_deep_equal(context.response.json(), context.expected_response)
