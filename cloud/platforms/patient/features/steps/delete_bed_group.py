import uuid

from behave import step, when

from app.common.models import BedGroup


@step("a request to delete group by id")
def step_impl(context):
    context.group_id_to_delete = "e73b8866-0ab7-4b9d-a287-04e147363ad5"
    context.request = {
        "url": "/patient/bed-group/DeleteBedGroup",
        "json": {"group_id": context.group_id_to_delete},
    }


@step("several bed groups exist, including the one to be deleted")
def step_impl(context):
    group_to_delete = BedGroup(
        id=uuid.UUID(context.group_id_to_delete),
        name="Group To Delete",
        description="Delete Me",
    )
    context.db.add(group_to_delete)

    context.other_ids = []
    for i in range(3):
        new_id = uuid.uuid4()
        context.other_ids.append(new_id)
        group = BedGroup(id=new_id, name=f"group-{i}", description=f"desc-{i}")
        context.db.add(group)

    context.db.commit()


@step("several bed groups exist, not including one to be deleted")
def step_impl(context):
    context.other_ids = []
    for i in range(3):
        new_id = uuid.uuid4()
        context.other_ids.append(new_id)
        group = BedGroup(id=new_id, name=f"group-{i}", description=f"desc-{i}")
        context.db.add(group)

    context.db.commit()


@when("the request is made to delete bed group by id")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the deleted bed group no longer exists")
def step_impl(context):
    deleted_group = context.db.get(BedGroup, context.group_id_to_delete)
    assert not deleted_group


@step("the other bed groups still exist")
def step_impl(context):
    groups_still_there = []
    for ident in context.other_ids:
        group = context.db.get(BedGroup, ident)
        groups_still_there.append(group)

    assert len(groups_still_there) == 3
