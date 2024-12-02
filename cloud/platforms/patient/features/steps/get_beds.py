import uuid

from behave import step, when

from app.common.models import Bed


@step("a request to get all beds")
def step_impl_1(context):
    context.encounters_by_bed_id = {}
    context.request = {"url": "/patient/bed"}


@when("the request to get all beds is made")
def step_impl_2(context):
    context.response = context.client.get(**context.request)
    context.db.expire_all()


@step("beds exist")
@step("{number:d} beds exist")
def step_impl_4(context, number: int = 2):
    context.beds = []
    for i in range(number):
        bed = Bed(id=uuid.uuid4(), name=f"Bed {i}")
        context.db.add(bed)
        context.beds.append(bed)
    context.db.commit()
    context.assigned_beds = context.beds


@step("all beds are returned")
def step_impl_5(context):
    response = context.response.json()
    assert "resources" in response
    resources = response["resources"]
    existing_beds_by_id = {str(b.id): b for b in context.beds}
    for resource in resources:
        bed_id = resource["id"]
        assert bed_id in existing_beds_by_id
        bed = existing_beds_by_id[bed_id]
        assert resource["name"] == bed.name
        expected_encounter = context.encounters_by_bed_id.get(str(resource["id"]))
        if expected_encounter:
            assert str(expected_encounter.id) == resource["encounter"]["id"]
            assert expected_encounter.status == resource["encounter"]["status"]
