import uuid

from behave import step


@step("a request to batch assign beds to a group")
def step_impl(context):
    context.group_id = str(uuid.uuid4())
    context.bed_ids = [str(uuid.uuid4()) for _ in range(3)]
    context.payload = [{"group_id": context.group_id, "bed_ids": context.bed_ids}]

    context.request = {
        "url": "/web/bed-group/beds/batch",
        "json": {"resources": context.payload},
    }


@step("a request to batch assign beds to multiple groups")
def step_impl(context):
    context.payload = []
    context.group_ids = [str(uuid.uuid4()) for _ in range(3)]
    for group_id in context.group_ids:
        context.bed_ids = [str(uuid.uuid4()) for _ in range(3)]
        context.payload.append({"group_id": group_id, "bed_ids": context.bed_ids})

    context.request = {
        "url": "/web/bed-group/beds/batch",
        "json": {"resources": context.payload},
    }
