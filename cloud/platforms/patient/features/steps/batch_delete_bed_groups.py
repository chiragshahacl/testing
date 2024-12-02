import uuid

from behave import step, when
from sqlalchemy import select
from starlette import status

from app.common.models import Bed, BedGroup
from app.settings import config


@step("a request to delete bed groups")
def step_impl(context):
    context.bed_groups_to_delete_ids = [group.get("id") for group in context.bed_groups]
    context.request = {
        "url": "/patient/bed-group/BatchDeleteBedGroups",
        "json": {"group_ids": context.bed_groups_to_delete_ids},
    }

    context.expected_code = status.HTTP_204_NO_CONTENT


@when("the request to batch delete bed groups is made")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the requested bed groups are deleted")
def step_impl(context):
    for bed_group_id in context.bed_groups_to_delete_ids:
        bed_group = context.db.get(BedGroup, bed_group_id)
        assert not bed_group


@step("the deletion of the bed groups is published")
def step_impl(context):
    context.producer.send_and_wait.assert_called()


@step("the deletion of the bed groups is not published")
def step_impl(context):
    context.producer.send_and_wait.assert_not_called()


@step("the bed groups to delete does not exists")
def step_impl(context):
    not_existing_bed_group_ids = [str(uuid.uuid4()) for _ in range(10)]
    context.request["json"] = {"group_ids": not_existing_bed_group_ids}


@step("no bed groups are deleted")
def step_impl(context):
    for group_id in context.bed_groups_to_delete_ids:
        group = context.db.get(BedGroup, group_id)
        assert group


@step("the groups have beds assigned")
def step_impl(context):
    stmt = select(BedGroup).where(BedGroup.id.in_(context.bed_groups_to_delete_ids))
    bed_groups = context.db.execute(stmt).scalars().all()
    context.beds = []

    for bed_group in bed_groups:
        beds_for_each_group = []
        for i in range(config.MAX_BEDS_PER_GROUP):
            bed = Bed(id=uuid.uuid4(), name=f"Bed {i} in {bed_group.name}")
            context.beds.append(bed)
            beds_for_each_group.append(bed)
            context.db.add(bed)

        context.db.commit()
        bed_group.beds = beds_for_each_group

    context.db.commit()


@step("the beds are not deleted")
def step_impl(context):
    bed_ids = [bed.id for bed in context.beds]
    for bed_id in bed_ids:
        bed = context.db.get(Bed, bed_id)
        assert bed


@step("the list of bed group to delete is empty")
def step_impl(context):
    context.request["json"] = {"group_ids": []}
