import uuid

from behave import step, when

from features.factories.observation_factories import ObservationFactory
from features.factories.patient_factories import PatientFactory


@step("a valid request to get patient observations")
def step_impl(context):
    context.patient_ids = [
        "4863b106-db56-47ad-a4b6-b70c0b63582c",
        "d93712c4-fd37-4ef9-8ff8-b29387b4fcb8",
        "62bccad5-2784-48a4-9513-3336b11a5bc0",
        "0bbd3c6f-d46d-4396-bfb2-930e3ba683bd",
        "ebb267a2-b264-408b-9d92-9921447c49b5",
    ]
    context.request = {"url": "/patient/observation"}


@step("the request is supplied query params for {num} of the existing observations")
def step_impl(context, num):
    context.expected_patient_ids = context.patient_ids[: int(num)]
    context.excluded_patient_ids = context.patient_ids[int(num) :]
    context.query_params = {"isAlert": True, "patientIds": context.expected_patient_ids}


@step(
    "the request is supplied query params for {num} of the existing observations and not an alert"
)
def step_impl(context, num):
    context.expected_patient_ids = context.patient_ids[: int(num)]
    context.excluded_patient_ids = context.patient_ids[int(num) :]
    context.query_params = {
        "isAlert": False,
        "patientIds": context.expected_patient_ids,
    }


@when("the request is made to get patient observations")
def step_impl(context):
    context.response = context.client.get(
        **context.request, params=getattr(context, "query_params", {})
    )


@step("several patient observations exist")
def step_impl(context):
    context.expected_observations = []
    context.observations = {}
    for patient_id in context.patient_ids:
        patient_uuid = uuid.UUID(patient_id)
        patient = PatientFactory.build(id=patient_uuid)
        context.db.add(patient)
        context.db.flush()
        for i in range(5):
            obs = ObservationFactory.build(
                subject_id=patient_uuid,
            )
            context.db.add(obs)
            context.db.flush()
            context.observations[obs.id] = obs
    context.db.commit()


@step("the expected patient observations are returned")
def step_impl(context):
    assert context.response.json()
    resp = context.response.json()
    for item in resp["resources"]:
        assert item["subject_id"] in context.expected_patient_ids
        assert item["subject_id"] not in context.excluded_patient_ids

        # Expected format
        item_id = item.get("id")
        assert context.observations[item_id].category == item.get("category")
        assert context.observations[item_id].code == item.get("code")
        assert str(context.observations[item_id].subject_id) == item.get("subject_id")
        assert context.observations[item_id].effective_dt.isoformat() == item.get("effective_dt")
        assert context.observations[item_id].value_text == item.get("value_text")
        assert context.observations[item_id].device_primary_identifier == item.get(
            "device_primary_identifier"
        )
        assert context.observations[item_id].device_code == item.get("device_code")
