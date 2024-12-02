import base64
import datetime
import json
import uuid

import jwt
from behave import step, then
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette import status
from test_tools import assert_deep_equal

from app.common.models import Bed, BedGroup, Patient
from app.patient.enums import GenderEnum
from app.settings import config
from features.factories.patient_factories import PatientFactory

JWT_SECRET_TOKEN = "secret"
CREATE_PATIENT_PARAM = json.dumps(
    {
        "entity_id": "7ab46f31-c98d-4c19-b720-798972787459",
        "event_name": "Patient Created",
        "performed_on": "2023-08-16T00:00:00",
        "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "event_state": {
            "id": "7ab46f31-c98d-4c19-b720-798972787459",
            "primary_identifier": "primary-identifier",
            "active": True,
            "given_name": "given",
            "family_name": "family",
            "gender": "male",
            "birth_date": "2020-03-29",
        },
        "previous_state": {},
        "entity_name": "patient",
        "emitted_by": "patient",
        "event_type": "PATIENT_CREATED_EVENT",
        "event_data": {
            "id": "7ab46f31-c98d-4c19-b720-798972787459",
            "primary_identifier": "primary-identifier",
            "active": True,
            "given_name": "given",
            "family_name": "family",
            "gender": "male",
            "birth_date": "2020-03-29",
        },
    }
)

CREATE_PATIENT_PARAM_WITHOUT_BIRTHDATE = json.dumps(
    {
        "entity_id": "7ab46f31-c98d-4c19-b720-798972787459",
        "event_name": "Patient Created",
        "performed_on": "2023-08-16T00:00:00",
        "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "event_state": {
            "id": "7ab46f31-c98d-4c19-b720-798972787459",
            "primary_identifier": "primary-identifier",
            "active": True,
            "given_name": "given",
            "family_name": "family",
            "gender": "male",
            "birth_date": None,
        },
        "previous_state": {},
        "entity_name": "patient",
        "emitted_by": "patient",
        "event_type": "PATIENT_CREATED_EVENT",
        "event_data": {
            "id": "7ab46f31-c98d-4c19-b720-798972787459",
            "primary_identifier": "primary-identifier",
            "active": True,
            "given_name": "given",
            "family_name": "family",
            "gender": "male",
            "birth_date": None,
        },
    }
)


def generate_token():
    now = datetime.datetime.now()
    exp = now + datetime.timedelta(days=1)
    token = {
        "token_type": "access",
        "exp": exp.timestamp(),
        "jti": "8daefa7b83d84a779112603dd1517fe7",
        "user_id": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "aud": "tucana",
    }
    return token


def generate_valid_jwt_token(context) -> str:
    key1 = base64.b64decode(LOCAL_PRIVATE_KEY).decode("utf-8")
    test_jwt = generate_token()
    token = jwt.encode(test_jwt, key=key1, algorithm="RS256")
    return f"Bearer {token}"


def generate_invalid_valid_jwt_token(context) -> str:
    ex_jwt = generate_token()
    token = jwt.encode(ex_jwt, key=FAKE_JWT_PRIVATE_KEY, algorithm="RS256")
    return f"Bearer {token}"


@step("the user is told the request was successful")
def step_impl(context):
    assert (
        status.HTTP_204_NO_CONTENT >= context.response.status_code >= status.HTTP_200_OK
    ), context.response.status_code


@step("the user is told the request was successful with no content")
def step_impl(context):
    assert context.response.status_code == status.HTTP_204_NO_CONTENT


@step("the user is told the request was unauthorized")
def step_impl(context):
    assert (
        context.response.status_code == status.HTTP_401_UNAUTHORIZED
    ), context.response.status_code


@step("the user is told the request was forbidden")
def step_impl(context):
    assert context.response.status_code == status.HTTP_403_FORBIDDEN, context.response.status_code


@step("the user is told there payload is invalid")
def step_impl(context):
    assert (
        context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), context.response.status_code


@step("the user is told the patient was not found")
def step_impl(context):
    assert context.response.status_code == status.HTTP_404_NOT_FOUND


@step("the user is told the patient with primary identifier already exists")
def step_impl(context):
    assert (
        context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), context.response.status_code
    assert context.response.json()["detail"][0]["type"] == "value_error.already_in_use"


@step("the request includes no `{field_name}` field")
def step_impl(context, field_name):
    context.mock_pubsub = False
    context.request["json"].pop(field_name, None)


@then("the user is told the bed group name is in use")
def step_impl(context):
    assert (
        context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), context.response.status_code
    assert_deep_equal(
        context.response.json(),
        {
            "detail": [
                {
                    "loc": ["body", "name"],
                    "msg": "Bed group name already exists. Change or enter a new one.",
                    "type": "value_error.already_in_use",
                    "ctx": {},
                }
            ]
        },
    )


@then("The response is an empty list")
def check_empty_list_response(context):
    assert_deep_equal(context.response.json(), [])


@step("the patient exists")
@step("the patient already exists")
def step_impl(context):
    patient = Patient(
        id=context.patient_id,
        primary_identifier=getattr(context, "patient_primary_identifier", "PX-001"),
        active=getattr(context, "patient_active", True),
        given_name=getattr(context, "patient_given_name", "Given"),
        family_name=getattr(context, "patient_family_name", "Family"),
        gender=GenderEnum[getattr(context, "patient_gender", "male").upper()],
        birth_date="2020-03-29",
    )
    context.db.add(patient)
    context.db.commit()
    context.db.refresh(patient)
    context.patient = patient


@step("the patient is created")
@step("the patient is updated")
@step("the patient is fetched")
def step_impl(context):
    patient = context.db.get(Patient, context.patient_id)
    assert patient
    assert str(patient.id) == context.patient_id
    assert patient.primary_identifier == context.patient_primary_identifier
    assert patient.active == context.patient_active
    assert patient.given_name == context.patient_given_name
    assert patient.family_name == context.patient_family_name
    assert patient.gender.value == context.patient_gender
    if hasattr(context, "patient_birthdate"):
        assert str(patient.birth_date) == context.patient_birthdate


@step("valid authentication credentials are being included")
def step_impl(context):
    context.internal_token = generate_valid_jwt_token(context)
    context.request["headers"] = {"Authorization": context.internal_token}


@step("invalid authentication credentials are being included")
def step_impl(context):
    context.internal_token = generate_invalid_valid_jwt_token(context)
    context.request["headers"] = {"Authorization": context.internal_token}


@step("the request specifies a `{name}` of `{value}`")
def step_impl(context, name, value):
    context.query_params = getattr(context, "query_params", {})
    context.query_params[name] = value


@step("there are `{number_of_patients}` patients")
def step_impl(context, number_of_patients: str):
    context.patients = []
    for i in range(int(number_of_patients)):
        patient = Patient(
            id=uuid.uuid4(),
            primary_identifier=f"P-00{i}",
            active=True,
            given_name="Name",
            family_name="Family",
            gender=GenderEnum.FEMALE,
            birth_date="2020-03-29",
        )
        context.db.add(patient)
        context.patients.append(patient)
    context.db.commit()


@step("the bed exists")
@step("the beds exist")
def step_impl(context):
    bed_group1 = BedGroup(id=uuid.uuid4(), name=f"Group 1")
    bed_group2 = BedGroup(id=uuid.uuid4(), name=f"Group 2")
    context.db.add(bed_group1)
    context.db.add(bed_group2)
    context.db.commit()
    bed_ids = context.bed_ids if hasattr(context, "bed_ids") else [context.bed_id]
    for index, bed_id in enumerate(bed_ids):
        bed = Bed(id=uuid.UUID(bed_id), name=f"Bed {index + 1}")
        bed.groups = [bed_group1, bed_group2]
        context.db.add(bed)
        context.db.commit()


@step("the bed group exist")
@step("the bed groups exist")
def step_impl(context):
    group_ids = context.group_ids if hasattr(context, "group_ids") else [context.group_id]
    for index, group_id in enumerate(group_ids):
        bed_group = BedGroup(id=uuid.UUID(group_id), name=f"Group {index}")
        context.db.add(bed_group)
        context.db.commit()


@step("the bed group is full")
@step("the bed group has `{number:d}` beds assigned")
def step_impl(context, number: int = config.MAX_BEDS_PER_GROUP):
    for group_id in context.group_ids:
        stmt = (
            select(BedGroup)
            .where(BedGroup.id == uuid.UUID(group_id))
            .options(selectinload(BedGroup.beds))
        )
        group = context.db.execute(stmt).scalars().one_or_none()
        context.assigned_beds = []
        for index in range(number):
            bed = Bed(id=uuid.uuid4(), name=f"Bed {index + 100}")
            context.db.add(bed)
            context.assigned_beds.append(bed)
        context.db.commit()
        group.beds = context.assigned_beds
        context.db.add(group)
        context.db.commit()


@then("the user is told the bed name is in use")
def step_impl(context):
    assert (
        context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), context.response.status_code
    assert_deep_equal(
        context.response.json(),
        {
            "detail": [
                {
                    "loc": ["body", "name"],
                    "msg": "Name already in use",
                    "type": "value_error.already_in_use",
                    "ctx": {},
                }
            ]
        },
    )


@then("the user is told the maximum amount of beds has been reached")
def step_impl(context):
    assert (
        context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    ), context.response.status_code
    assert_deep_equal(
        context.response.json(),
        {
            "detail": [
                {
                    "loc": ["body"],
                    "msg": (
                        "You have reached the maximum "
                        f"number of beds for the system ({config.MAX_BEDS})."
                    ),
                    "type": "value_error.too_many_beds",
                    "ctx": {},
                }
            ]
        },
    )


@step("the user is told the bed was not found")
def step_impl(context):
    assert context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_deep_equal(
        context.response.json(),
        {
            "detail": [
                {
                    "loc": ["body"],
                    "msg": "Bed not found.",
                    "type": "value_error.not_found",
                    "ctx": {},
                }
            ]
        },
    )


@step("the user is told the primary identifier is already used")
def check_pid_already_used(context):
    assert context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_deep_equal(
        context.response.json(),
        {
            "detail": [
                {
                    "loc": ["body", "primary_identifier"],
                    "msg": "Primary identifier already in use",
                    "type": "value_error.already_in_use",
                    "ctx": {},
                }
            ]
        },
    )


@step("the user is told the bed group name is not found")
def step_impl(context):
    assert context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_deep_equal(
        context.response.json(),
        {
            "detail": [
                {
                    "loc": ["body", "group_id"],
                    "msg": "Bed group not found.",
                    "type": "value_error.not_found",
                    "ctx": {},
                }
            ]
        },
    )


@step("the user is told the bed group is full")
def step_impl(context):
    assert context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_deep_equal(
        context.response.json(),
        {
            "detail": [
                {
                    "loc": ["body", "group_id"],
                    "msg": (
                        f"You have reached the maximum number "
                        f"of beds for the system ({config.MAX_BEDS})."
                    ),
                    "type": "value_error.bed_group_full",
                    "ctx": {},
                }
            ]
        },
    )


@step("the user is told the bed is assigned to the group")
def step_impl(context):
    assert context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_deep_equal(
        context.response.json(),
        {
            "detail": [
                {
                    "loc": ["body", "group_id"],
                    "msg": "Bed already assigned to a group",
                    "type": "value_error.already_in_use",
                    "ctx": {},
                }
            ]
        },
    )


LOCAL_PRIVATE_KEY = (
    "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpN"
    "SUlKS0FJQkFBS0NBZ0VBcHlEaC9BSllFdXFuMlRGVXhqa"
    "zc5eno2V1VGcmJ3Rk5DaFdyWWUvY3ROK3ZpdnJVCnVPak"
    "t6YXFHZ3VwT0tKclZlSE8wMTJkM1ZrRGozM1p1QzROd2x"
    "xZjYvOUY4QnFCd3BoWHVsNkhOelB6YmdBL28KbUdBN1I4"
    "aXZpZ2l3VC8rY2lseEJ4V004WFdFRmZNTmdCdGhVbGtDe"
    "FB5MnRkRjNJNTdTbVBtUzdhNjNsZ3RWTgpxSXZvMVdVVl"
    "IzeVpPelA4OGU1Y0FsTXZYaGkvTmMrZFlTckZZdVpON1F"
    "wbTJCMmVIQzVmQlI4TXFRQ0lWL2JvCjdoVmx3d2R6dll5"
    "WkdkN3p4dzNwVERGYXliSjcxVmh2Nk5oVmpYdkIrckVDT"
    "W9KMWFxRExjdkFwcE1yT29wUkMKRjZxR0pUZDRobWhlUE"
    "NQc3kvb3V0TnFhOVNHK3VxSlVFR29tSjNyaGJadzdJdlo"
    "3T0VSQXN2eE9rbCs4MVNjcQo3elIrb0pEN0RzTFcvOFBv"
    "RXlsMnc4b1dyWkNWZTRjNFNUL2dKOGxlVDlBbkNBcnN1Q"
    "VpDR2JJZ3B2MnRDKzVyCnAwZTRkR3JGdlRoNVpaVmx6b2"
    "pvOW1JdmNTZHlZRGFiY0dMZTEzNmgwU1VjNDNYbDJrTXl"
    "aRDUrN2ZoelNMMkMKVjhQM282eE0rb1c1NlJ3QjE5S1BP"
    "cVZ3Uit0eVBTVE1MMXpaTGw5bmkvbW1ndk1uTTQrTlpkM"
    "FliaXZ3Zy9GaAp6RkRrT2dwVEtmNWNvU2Z1SUpPYmtieT"
    "NNZ2MzM3NWQm1JZ2dXNnFjR2tzNFlEVC9SSEY1ZUZFNm5"
    "2YVZTMy9pCnpOTmY0eFQvZTQ5dHRweG9MSTZNc0Fub2Zp"
    "Q0YwS0d4b1FiNUU0YnlndXRieS94NUh3NmJNNm9PeDZzQ"
    "0F3RUEKQVFLQ0FnQWtkSnhHdzk0aFZqVkJ2Nng5eHF0Sm"
    "JYQXdld0FyeVExY2QwaVlodUZPUlFLK0hxTzdKL0JnOTJ"
    "MNgorSkFPOUdNL01JSVFnSDI3LzFDVmhIaFJvNXl5Q0Rk"
    "TWlRMzBSaGY4YW9sT1l4bUlydGxVY0dQc3BRVVpUZkhZC"
    "mVyZTI0NHRxZE9CVjVhVWJ1MWVlbE9HRDdMbGF3d2JHd0"
    "xoMnl5UlJRb3NHemlOQnhEOXRrQWl1RE1LL2xacVUKS3Q"
    "0ajExM0VDaG5nMmZOWm82MUYyQ0U4dWo4dktReHplZExn"
    "TG1tNFBQYzJIMFU4TWlVTGh3emRMaWF4NlpTNgpFb3FzN"
    "VlDb2VXVGIzV0l2My9KNklaM2JuU0RnU1ZBUlZuNGp0V2"
    "hXVjNlNWZTQ2dWU3JJdE8xTHkwTVNxQ3h1CnFTSnhIT2N"
    "Bd1hSaHQ5T1lTQUdhSldHUDZRK2tMMmRSOEJTdTVoU1U4"
    "ZVR3VDhCTitaRlNXWmlLWXdPNlkrTkYKbXZLemN2cUFJU"
    "EtYRFhUYTlWZjVPcG41Q0t4SHpmU3ozalViemtNZ1lBNz"
    "FRMWFxYzZQT2xaYnI0dWxJd2pPdApRWDdvV0o2K2Y5QUd"
    "QUFdwQ3pnNFpMWXFUeE12dVBTYi9ia2Ixcks5U1NIUVB1"
    "OElEb1I1M1E4OUN0VVZWWnhRCnlyY2xCUkR4ZFNjeEo4b"
    "Ww2ajBzRVY4V2FjK1FhTG1xM0E2cDJZeHhmMnZDUVhybG"
    "Fnb3RnZnRxdW9mcUZZWSsKWEdkOEdVN0pSaFZZNDZwbzh"
    "hYSt1dHptV0tobERYSHdnODBvZFhnR0RQbjlUK2d1QUZ2"
    "MWJlNXpJeFhNWWZ5eApWQ2x4WlJTRk9HeENOTkZjVEVGO"
    "DdSSGRiMGtMR0t0MTFMdWpNWUNyVmJ0UW5WSXlxUUtDQV"
    "FFQTRlUGp0bStRCjBmK290emFYTnpkaGU4ZFNoL1Nicyt"
    "XYVhOK0xvK1BCOVdPYVY0andaWVVjSFlDZEFGKzhrdTdC"
    "QXN4dlBHTnIKMmExVkJXSmFHN1dVNktVaW1xaG1pcUNNb"
    "mpSdzVoazhLeHNrY0xJM2laRFZINm5aR0hPQlZuSkphWD"
    "grZ2c3Sgo4a0o3VXY4SHhQY0g0VDJvSVphUWlkUEtsQXp"
    "xUVR2MTM3YUVweTZ4TjRlenlZUGpsYzU2bWYyL2VDU25S"
    "TktMClNsZWpQN2lsWWhFQ3FXalh2UmVrOCtKYU55S2JSO"
    "FQ2TC9kenRsZWc2NHlPMTkyUks3SXF4WlFIZ3luZllqN1"
    "MKdGkxME8xUjFCdm5sOVFMOGN2OWYwYkltc00xTU52dDR"
    "ZazJMajdEalZhLytmTlAxNlBONHd2UlFXOVc0RzBwWApy"
    "UmxZQjYzaUh1WUJvd0tDQVFFQXZXZlp5M1d2alI0dUwrQ"
    "m9HU054M0t5WnNwQkFDMnFiN1pNd2ovT1F6QUNZCjlOWV"
    "NObHYvcXdiSWxGZy9SRXNqTko4bWFQY013MEFsTlovTmx"
    "nc2Y3L0I1bzNZQ0lKT2xGWVpiZGEyRVhqcXIKc2tGNHFE"
    "ZC9LQVYrSHRGSmJ2cTEwVGtWY216Q1F5SVR5bkM5L3UzM"
    "npvRGxUWEJFU3grT1h3bHR4YkEvcmd0NQpkRmJuNlRCWl"
    "phN3pjcWlCUlBCNGlwK0w1ZHZrckdWalQrZzBtVmdVQ21"
    "2USs5OXBNN2Z1Wk56NzhGYXhIZmRCCmU2RlpFUkxxcStw"
    "aHhWNkUzQ0pOWHJOZXhtSUgzWmk1SHBZVHZYcnppWEF1T"
    "VE0aWNDbGN6Y0xCNHhlT3F3Z2QKcVVjbExQK0tmVXVpUD"
    "ZMMGtvUjl6SXBzWWIrSEhGU2gvdUkrejBaU1dRS0NBUUF"
    "ZQU5OTnE0VkVDMXF1UFVyTQpQMEpJbU9HWU9OSGl4OThq"
    "UjAzYldIUmYwdm12bTRtUUFCa0F1WTMxWURiMWxoRkVid"
    "HpUR2UxMzhBYzh6enFyCi94dVhyUlNFUXFqQ3lsU202d0"
    "9rTDhKSkFsVlk5RmNhY3gxeWcrWGh4MFJUSDBuVndBT3d"
    "aa25uU0ZFNmZJY2kKMHUwdmJoSFRuK0EwQlNGZG9oR3la"
    "T0MzcVBsbm1ucVNZQVVtd0xFS1ZpcUkrb0hDRG9NSHVTZ"
    "TcrcHdLUldDdApqd2t0WDBxdGVUbTZBSzk5ZEZ2endHYW"
    "xlakg5aWtvN1BYQmdWOWI1UWJGeDFVMEhEd2dCdEpOSGN"
    "JVU5XT2dtCm1aOXA3YXROdlAwOWx5U3RYT05nWkZCaWdj"
    "TDJ2ZUVxVmMxQkRuVHZFQkFoQnowU3hSOFBKMU14dmFPe"
    "ERUVWQKKzJycEFvSUJBUUMydi9jekN2QkJsdmMxbHE2YV"
    "lzckFBNEdnK3ZId2tnSzFiaW1URzQyQWFLc3N3VWg5VHJ"
    "NWApUOHBFNkFqVFdqUXoxOE4xejdsdXd2dWtDL2FQYVZo"
    "OWFHZlZRazIzSlA1S0VJTTZ2aHRUMkFSR1VFbWM5VDhwC"
    "lhITmVSTTAzMll1SXZpMWxaRzdqMjRPQTl0czdtRnRrME"
    "pWdTdIM1loakFXbnNCZDJEcjVNWFVVdmEyeUg4YUMKQ0J"
    "ZNWNVQ1pSZlRvdkJ4OXduZVhwNVAxUzdWRXArbGVUTDB0"
    "NlZoV1lJZ1NwZTRvN1Z5ajd5Z3RvM2FPdE5QYwo0SjlKa"
    "25OYSszWHZnOTVVUjg0VEVBSzk4a3hGck5aQ3JBekZwRC"
    "t5UFJhZ0tlUnR1eE1iRHcrZmYxZnRYUHRBCi9iTWs5NVJ"
    "Ic3JLMm9uRUV0NG9qMmIwY2N5dnJUb3l4QW9JQkFEamZ3"
    "WjIxZWRQL1ZCMFlIMHo0bGM5b3pUT0YKbXg5M21XTDZyN"
    "jF0NmpVT09zZTRuNE4wZERtbWJRY0h5V21FWTkvMVdDbz"
    "F6L3RBMC91OS9tQzZNYkVoQjEraApGOUFCQWRZN1dpcnV"
    "zYkJZakFldSt2NWlOMTVXYUwrVURQb0I3Wjc5S00rZVVV"
    "OWc4TUI3a3VCYmJiMm00SzUrCjlpWDdkT3hYRkRFeHQxM"
    "zh4eFAvK1p2UG1UNDBOajIrUllndHNsR25zbXNPeVk0dm"
    "0rYk82MnZMMDd3UzlObysKR0lZSjhyMVNiVUZrWnpnaWU"
    "1WkhwM28yd3J2Vy9GajlWWlBxbGhGQ2V4TUdYMTlybm5P"
    "ZW4zcW01MlFGS0MxZgorbjZHZEVzdGdiNXVKeUtseGZqe"
    "DQwNDJBZGFORXJKUjZLNmdMZXpVK2Y0aTNCQzNrUzZpYm"
    "VhOGQ1cz0KLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0"
    "tLS0K"
)


FAKE_JWT_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDUgDY89yX2DU026ASRMEA+lIRHd5lD+4Wcv1etudmqHnO2iEKO
TubdUMLanNv4OEAkOCL2QO37+xEyOJaztqeykHpx8S3XR2FUoCRb7RpPdaTBFh5e
Je306ZyA2MjrMI2GVKBshmKgToPg3TtxwOevJ1dNTSnH4zae2UAEpFbdhQIDAQAB
AoGBAJL2CIypMCu2j0wFsgLnJ8cf10vFvs1xSbpZ6j1PZuVsIgJ+wejBUJCGpfui
t842uMVTvXoo9W1q+T2OPUsUa2ykBfBeLBfgA7di4mpQcHGld+JD4ymPlEwW+fuM
TKVoYIBRj4R7MtXPGFYdTTpnKXSbN3c5jfcXnp8DPLPzEYeRAkEA8bVUzGNGWFk3
7T/beIgWj5Bf9Q6aZHohHa9/zFILzZVPEiv99xGK2fToW+ds1F6n3ksWESagfAGN
h18zVKg2qwJBAOEQxnRFO+S7TLdyOF4wSvwfIpfkYM5R5Qn/1RHuRDC2VMEWwA9D
nN29JMzzRzWUMM6pYXRrh4blO2wnw42w/I8CQQCRTfdKX6vcVNZANBFWJkmZyKtH
AJ5kJN9fny9uvywFTOsZ+4RTUSJt4MMG7NsJ2FWGVxFPAi+cHLreVKbhD7a9AkAN
YuwK2ltXnXRQrPCBWan8GPX7xs+jNefDkn3f1SYlJ5Me8PV3cvQPlEJuFkI0A55r
jFOJkyO6eEPyiOLuuIotAkAESIKxaC4vSNH46H8XphGOHu1W5WXqnOYUZMiIh33G
qN+N9AJtoHPFN2GU36eKg57A55bJ4V1T4NfJKd1EMi2O
-----END RSA PRIVATE KEY-----"""


def assert_message_was_published(
    context, topic: str, value: dict, headers: list[tuple[str, bytes]]
):
    found = False
    for call_args, call_kwargs in context.producer.send_and_wait.call_args_list:
        actual = json.loads(call_kwargs["value"])
        found = all(
            [
                not call_args,
                call_kwargs["topic"] == topic,
                actual == value,
                call_kwargs["headers"] == headers,
            ]
        )
        if found:
            break
    assert found, "Mock call not found"


@step("A patient exists")
def add_patient(context):
    context.patient = PatientFactory()
    context.db.add(context.patient)
    context.db.commit()
