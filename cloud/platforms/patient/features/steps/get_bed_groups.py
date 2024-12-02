import uuid

from behave import step, when
from sqlalchemy import insert

from app.common.models import BedGroup


@step("a valid request to get bed groups")
def step_impl(context):
    context.request = {"url": "/patient/bed-group"}


@step("bed groups exist")
@step("{number:d} bed groups exist")
def step_impl(context, number: int = 2):
    context.bed_groups = [
        {"id": str(uuid.uuid4()), "name": f"Bed Group {i}"} for i in range(number)
    ]
    context.db.execute(insert(BedGroup), context.bed_groups)
    context.db.commit()


@when("the request is made to get bed groups")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("the existing bed groups are returned")
def step_impl(context):
    result = context.response.json()
    assert "resources" in result
    resources = result["resources"]
    assert len(resources) == len(context.bed_groups)
    found_bed_groups_by_id = {bg["id"]: bg for bg in resources}
    for bed_group in context.bed_groups:
        bed_group_id = bed_group["id"]
        assert bed_group_id in found_bed_groups_by_id
        found_bed_group = found_bed_groups_by_id[bed_group_id]
        assert bed_group["name"] == found_bed_group["name"]
        assert bed_group.get("description") == found_bed_group.get("description")
        assert "beds" in found_bed_group


@step("no bed groups are returned")
def step_impl(context):
    result = context.response.json()
    assert "resources" in result
    assert result["resources"] == []
