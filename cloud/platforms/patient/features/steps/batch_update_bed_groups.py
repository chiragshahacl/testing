import uuid

from behave import step, then, when
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette import status

from app.common.models import Bed, BedGroup
from app.settings import config


@step("a request to batch update bed groups")
@step("a request to batch update `{number:d}` bed groups")
def step_impl(context, number: int = 2):
    context.bed_groups = [
        {
            "id": str(uuid.uuid4()),
            "name": f"Updated Bed Group {i + 1}",
            "description": f"Wonderful bed group {i + 1}",
        }
        for i in range(number)
    ]
    context.request = {
        "url": "/patient/bed-group/BatchUpdateBedGroups",
        "json": {"groups": context.bed_groups},
    }


@step("the bed groups to be updated exist")
def step_impl(context):
    bed_groups = context.bed_groups
    for index, group in enumerate(bed_groups):
        context.db.add(
            BedGroup(
                id=uuid.UUID(group["id"]),
                name=f"Bed group {index}",
            )
        )
    context.db.commit()


@when("the request to batch update bed groups is made")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the requested bed groups are updated")
def step_impl(context):
    found_groups = context.db.execute(select(BedGroup)).scalars().all()
    found_groups_by_id = {str(group.id): group for group in found_groups}
    expected_bed_groups = context.bed_groups
    assert len(expected_bed_groups) == len(found_groups)
    for group in expected_bed_groups:
        group_id = group["id"]
        assert group_id in found_groups_by_id
        found_group = found_groups_by_id[group_id]
        assert found_group.name == group["name"], f"{found_group.name} != {group['name']}"
        assert (
            found_group.description == group["description"]
        ), f"{found_group.description} != {group['description']}"


@step("the update of the bed groups is published")
def step_impl(context):
    context.producer.send_and_wait.assert_called()


@step("the bed group number `{number:d}` exist")
def step_impl(context, number: int):
    bed_group = BedGroup(
        id=uuid.UUID(context.request["json"]["groups"][number]["id"]),
        name=f"Bed group {number}",
    )
    context.db.add(bed_group)
    context.db.commit()


@then("the user is told the bed group was not found")
def step_impl(context):
    assert context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert context.response.json() == {
        "detail": [
            {
                "loc": ["body", "group_id"],
                "msg": "Bed group not found.",
                "type": "value_error.not_found",
                "ctx": {},
            }
        ]
    }


@step("the requested bed groups are not updated")
def step_impl(context):
    found_bed_groups = context.db.execute(select(BedGroup)).scalars().all()
    found_bed_groups_by_id = {str(group.id): group for group in found_bed_groups}
    for group in context.bed_groups:
        if group["id"] in found_bed_groups_by_id:
            bed_group_name = found_bed_groups_by_id[group["id"]].name
            bed_group_description = found_bed_groups_by_id[group["id"]].description
            assert group["name"] != bed_group_name
            assert group["description"] != bed_group_description


@step("the update of the bed groups is not published")
def step_impl(context):
    context.producer.send_and_wait.assert_not_called()


@step("one of the provided names is already in use by another bed group")
def step_impl(context):
    bed_group = BedGroup(
        id=uuid.uuid4(),
        name=context.bed_groups[0]["name"],
    )
    context.db.add(bed_group)
    context.db.commit()


@step("the bed groups have beds assigned")
def step_impl(context):
    bed_groups_to_update_ids = [group["id"] for group in context.bed_groups]
    stmt = select(BedGroup).where(BedGroup.id.in_(bed_groups_to_update_ids))
    bed_groups = context.db.execute(stmt).scalars().all()
    context.beds = []
    context.beds_by_group = []

    for bed_group in bed_groups:
        beds_for_each_group = []
        for i in range(config.MAX_BEDS_PER_GROUP):
            bed = Bed(id=uuid.uuid4(), name=f"Bed {i} in {bed_group.name}")
            context.beds.append(bed)
            beds_for_each_group.append(bed)
            context.db.add(bed)

        context.db.commit()
        bed_group.beds = beds_for_each_group
        context.beds_by_group.append({bed_group.id: beds_for_each_group})

    context.db.commit()


@step("the beds still assigned to the bed group")
def step_impl(context):
    for elem in context.beds_by_group:
        for group_id, beds in elem.items():
            stmt = (
                select(BedGroup).where(BedGroup.id == group_id).options(selectinload(BedGroup.beds))
            )
            bed_group = context.db.execute(stmt).scalars().first()
            assigned_beds = [bed.id for bed in bed_group.beds]

            for bed in beds:
                assert bed.id in assigned_beds
