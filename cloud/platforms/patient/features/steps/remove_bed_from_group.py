from behave import step

from app.common.models import Bed, BedGroup


@step("a request to remove bed from a group")
def step_impl(context):
    context.group_id = "1ed5bef9-6c89-4acc-acef-eae7fcfdf31d"
    context.bed_id = "ecd23ef2-8c95-4ce0-b154-5cf07371283d"
    context.request = {
        "url": "/patient/bed-group/RemoveBed",
        "json": {"bed_id": context.bed_id, "group_id": context.group_id},
    }


@step("the request to remove bed from a group is made")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the bed is part of the group")
def step_impl(context):
    bed = context.db.get(Bed, context.bed_id)
    group = context.db.get(BedGroup, context.group_id)
    group.beds.append(bed)
    context.db.commit()
    group = context.db.get(BedGroup, context.group_id)
    assert bed in group.beds


@step("the bed is removed from the group")
def step_impl(context):
    bed = context.db.get(Bed, context.bed_id)
    group = context.db.get(BedGroup, context.group_id)
    assert bed not in group.beds


def get_bed_and_group(context, group_id, bed_id):
    bed = context.db.get(Bed, bed_id)
    group = context.db.get(BedGroup, group_id)
    return bed, group
