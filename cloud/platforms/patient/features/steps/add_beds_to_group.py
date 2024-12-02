import uuid

from behave import step, when
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.common.models import BedGroup


@step("a request to add bed to a group")
def step_impl(context):
    context.group_id = "1ed5bef9-6c89-4acc-acef-eae7fcfdf31d"
    context.group_ids = [context.group_id]
    context.bed_id = "ecd23ef2-8c95-4ce0-b154-5cf07371283d"
    context.request = {
        "url": "/patient/bed-group/AddBed",
        "json": {"bed_id": context.bed_id, "group_id": context.group_id},
    }


@when("the request to add bed to a group is made")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the bed is assigned to the group")
def step_impl(context):
    stmt = select(BedGroup).join(BedGroup.beds).where(BedGroup.id == uuid.UUID(context.group_id))
    bed_group = context.db.execute(stmt).scalars().first()
    assert bed_group
    found_bed_ids = {str(bed.id) for bed in bed_group.beds}
    assert context.bed_id in found_bed_ids


@step("the bed is not assigned to the group")
def step_impl(context):
    stmt = (
        select(BedGroup)
        .where(BedGroup.id == uuid.UUID(context.group_id))
        .options(selectinload(BedGroup.beds))
    )
    bed_group = context.db.execute(stmt).scalars().first()
    assert bed_group
    found_bed_ids = {str(bed.id) for bed in bed_group.beds}
    assert context.bed_id not in found_bed_ids
