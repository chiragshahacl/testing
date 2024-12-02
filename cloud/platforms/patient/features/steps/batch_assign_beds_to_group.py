import uuid

from behave import step, then, when
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.common.models import Bed, BedGroup


@step("a request to batch assign beds to a group")
@step("a request to batch assign `{number:d}` beds to a group")
def step_impl(context, number: int = 2):
    context.group_ids = [str(uuid.uuid4())]
    context.beds_by_group_id = {
        group_id: [str(uuid.uuid4()) for _ in range(number)] for group_id in context.group_ids
    }
    context.request = {
        "url": "/patient/bed-group/BatchAssignBeds",
        "json": {
            "resources": [
                {"group_id": group_id, "bed_ids": context.beds_by_group_id[group_id]}
                for group_id in context.group_ids
            ]
        },
    }


@step("a request to batch assign beds to multiple groups")
def step_impl(context):
    context.group_ids = [str(uuid.uuid4()) for _ in range(2)]
    context.beds_by_group_id = {
        group_id: [str(uuid.uuid4()) for _ in range(2)] for group_id in context.group_ids
    }
    context.request = {
        "url": "/patient/bed-group/BatchAssignBeds",
        "json": {
            "resources": [
                {"group_id": group_id, "bed_ids": context.beds_by_group_id[group_id]}
                for group_id in context.group_ids
            ]
        },
    }


@when("the request to batch assign beds to a group is made")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the beds are the only ones assigned to the group")
def step_impl(context):
    for group_id in context.group_ids:
        expected_beds_ids = context.beds_by_group_id[group_id]
        stmt = (
            select(BedGroup)
            .where(BedGroup.id == uuid.UUID(group_id))
            .options(selectinload(BedGroup.beds))
        )
        bed_group = context.db.execute(stmt).scalars().first()
        assert bed_group
        assert len(bed_group.beds) == len(expected_beds_ids)
        for bed in bed_group.beds:
            assert str(bed.id) in expected_beds_ids


@step("the beds are assigned to the group")
def step_impl(context):
    for group_id in context.group_ids:
        expected_beds_ids = context.beds_by_group_id[group_id]
        stmt = (
            select(BedGroup)
            .where(BedGroup.id == uuid.UUID(group_id))
            .options(selectinload(BedGroup.beds))
        )
        bed_group = context.db.execute(stmt).scalars().first()
        assert bed_group
        found_bed_ids = {str(bed.id) for bed in bed_group.beds}
        for bed_id in expected_beds_ids:
            assert bed_id in found_bed_ids


@step("the bed group beds exist")
def step_impl(context):
    counter = 0
    for group_id in context.group_ids:
        for bed_id in context.beds_by_group_id[group_id]:
            bed = Bed(id=uuid.UUID(bed_id), name=f"Bed {counter}")
            context.db.add(bed)
            counter += 1
    context.db.commit()


@then("the beds are not assigned to the group")
def step_impl(context):
    for group_id in context.group_ids:
        stmt = (
            select(BedGroup)
            .where(BedGroup.id == uuid.UUID(group_id))
            .options(selectinload(BedGroup.beds))
        )
        group = context.db.execute(stmt).scalars().one_or_none()
        assert not group.beds
