import uuid

from behave import step, then, when

from src.common.models import InternalAudit


@step("a request to get audit trail for entity with id `{entity_id}`")
def request_audit_trail_by_id(context, entity_id):
    context.entity_id = entity_id
    context.record_id = 4
    context.data = {}
    context.timestamp = "2023-02-08 00:00:00"
    context.request = {"url": f"/audit-trail/{entity_id}"}
    context.emitted_by = "device"
    context.performed_by = "user"
    context.event_name = "Device created"
    context.event_type = "DEVICE_CREATED_EVENT"
    context.event_data = {}


@step("some audit trails exist")
def check_audit_trail_exists(context):
    audit_event = InternalAudit(
        id=context.record_id,
        entity_id=context.entity_id,
        data=context.data,
        timestamp=context.timestamp,
        emitted_by=context.emitted_by,
        performed_by=context.performed_by,
        event_name=context.event_name,
        event_type=context.event_type,
        message_id=str(uuid.uuid4()),
        event_data=context.event_data,
    )
    context.db.add(audit_event)
    context.db.commit()


@step("multiple audit trails exist")
def check_multiple_audit_trail_exists(context):
    audit_event = InternalAudit(
        id=context.record_id,
        entity_id=context.entity_id,
        data=context.data,
        timestamp=context.timestamp,
        emitted_by=context.emitted_by,
        performed_by=context.performed_by,
        event_name=context.event_name,
        event_type=context.event_type,
        message_id=str(uuid.uuid4()),
        event_data=context.event_data,
    )
    context.db.add(audit_event)
    dates = ["2022-02-08 00:00:00", "2023-03-08 00:00:00", "2023-02-09 00:00:00"]
    for i, date in enumerate(dates):
        event = InternalAudit(
            id=i,
            entity_id=context.entity_id,
            data=context.data,
            timestamp=date,
            emitted_by=context.emitted_by,
            performed_by=context.performed_by,
            event_name=context.event_name,
            event_type=context.event_type,
            message_id=str(uuid.uuid4()),
            event_data=context.event_data,
        )
        context.db.add(event)
    context.db.commit()


@when("the request for audit trails is made")
def request_audit_trail(context):
    context.response = context.client.get(**context.request)


@then("the list of all audit events are returned")
def check_audit_trail_returned(context):
    audit_event = context.db.get(InternalAudit, context.record_id)
    assert audit_event
    assert audit_event.id == context.record_id
    assert audit_event.entity_id == context.entity_id
    assert str(audit_event.timestamp) == context.timestamp
    assert audit_event.data == context.data
    assert audit_event.event_type == context.event_type
    assert audit_event.message_id
    assert audit_event.event_data == context.event_data


@step("the list of events is sorted")
def check_event_stored(context):
    resp = context.response.json()["resources"]

    assert resp == sorted(resp, key=lambda k: k["timestamp"], reverse=True)
