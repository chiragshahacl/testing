import uuid

from behave import step, when
from starlette import status

from app.common.models import Bed, BedGroup


@step("beds have been created in the system")
def step_impl(context):
    context.beds_to_delete = [Bed(id=uuid.uuid4(), name=f"Bed {i}") for i in range(10)]
    context.beds_to_delete_ids = [str(bed.id) for bed in context.beds_to_delete]

    for bed in context.beds_to_delete:
        context.db.add(bed)

    context.db.commit()


@step("a request to delete beds")
def step_impl(context):
    context.request = {
        "url": "/patient/bed/BatchDeleteBeds",
        "json": {"bed_ids": context.beds_to_delete_ids},
    }

    context.expected_code = status.HTTP_204_NO_CONTENT


@when("the request to batch delete beds is made")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the requested beds are deleted")
def step_impl(context):
    for bed_id in context.beds_to_delete_ids:
        bed = context.db.get(Bed, bed_id)
        assert not bed


@step("the deletion of the beds is published")
def step_impl(context):
    context.producer.send_and_wait.assert_called()


@step("the deletion of the beds is not published")
def step_impl(context):
    context.producer.send_and_wait.assert_not_called()


@step("the beds to delete does not exists")
def step_impl(context):
    not_existing_bed_ids = [str(uuid.uuid4()) for _ in range(10)]
    context.request["json"] = {"bed_ids": not_existing_bed_ids}


@step("no beds are deleted")
def step_impl(context):
    for bed_id in context.beds_to_delete_ids:
        bed = context.db.get(Bed, bed_id)
        assert bed


@step("the list of bed to delete is empty")
def step_impl(context):
    context.request["json"] = {"bed_ids": []}


@step("beds are assigned to a group")
def step_impl(context):
    context.bed_group = BedGroup(
        id=uuid.uuid4(),
        name="Bed group",
    )
    context.bed_group.beds = context.beds_to_delete
    context.db.add(context.bed_group)
    context.db.commit()


@step("the bed group is not deleted")
def step_impl(context):
    bed_group = context.db.get(BedGroup, context.bed_group.id)
    assert bed_group
