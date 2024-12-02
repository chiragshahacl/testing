import base64
import datetime
import json

import jwt
from behave import given, step
from sqlalchemy.orm import Session
from starlette import status

from app.common.event_sourcing.schemas import EventSchema
from app.device.src.common.models import Device, DeviceAlert
from app.device.src.device.schemas import VitalRange
from features.factories.device_factories import (
    DeviceAlertFactory,
    DeviceFactory,
    DeviceVitalRangeFactory,
)


def generate_token_example():
    now = datetime.datetime.now()
    exp = now + datetime.timedelta(days=1)
    token = {
        "token_type": "access",
        "exp": exp.timestamp(),
        "iat": now.timestamp(),
        "jti": "8daefa7b83d84a779112603dd1517fe7",
        "user_id": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "aud": "tucana",
    }
    return token


def generate_valid_jwt_token(context) -> str:
    key1 = base64.b64decode(LOCAL_PRIVATE_KEY).decode("utf-8")
    test_jwt = generate_token_example()
    token = jwt.encode(test_jwt, key=key1, algorithm="RS256")
    return f"Bearer {token}"


def generate_invalid_valid_jwt_token(context) -> str:
    test_jwt = generate_token_example()
    token = jwt.encode(test_jwt, key=FAKE_JWT_PRIVATE_KEY, algorithm="RS256")
    return f"Bearer {token}"


@given("the application is running")
def step_impl(context):
    pass


@step("the user is told the device was not found")
@step("the user is told the device group was not found")
def step_impl(context):
    assert context.response.status_code == status.HTTP_404_NOT_FOUND


@step("the device exists")
def step_impl(context):
    device = Device(
        id=context.device_id,
        primary_identifier=context.device_primary_identifier,
        name=context.device_name,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    context.db.add(device)
    context.db.flush()
    create_alarms_and_vitals(device, context.db)
    context.db.commit()


@step("A device exists")
def step_impl(context):
    device = DeviceFactory()
    context.db.add(device)
    context.db.commit()
    context.device = device


LOCAL_PRIVATE_KEY = (
    "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlKS0FJQkFBS0NBZ0VBcHlEaC9BSllFdXFuMlRGVXhqazc5eno2V1V"
    "GcmJ3Rk5DaFdyWWUvY3ROK3ZpdnJVCnVPakt6YXFHZ3VwT0tKclZlSE8wMTJkM1ZrRGozM1p1QzROd2xxZjYvOUY4QnFCd3BoWH"
    "VsNkhOelB6YmdBL28KbUdBN1I4aXZpZ2l3VC8rY2lseEJ4V004WFdFRmZNTmdCdGhVbGtDeFB5MnRkRjNJNTdTbVBtUzdhNjNsZ"
    "3RWTgpxSXZvMVdVVlIzeVpPelA4OGU1Y0FsTXZYaGkvTmMrZFlTckZZdVpON1FwbTJCMmVIQzVmQlI4TXFRQ0lWL2JvCjdoVmx3"
    "d2R6dll5WkdkN3p4dzNwVERGYXliSjcxVmh2Nk5oVmpYdkIrckVDTW9KMWFxRExjdkFwcE1yT29wUkMKRjZxR0pUZDRobWhlUEN"
    "Qc3kvb3V0TnFhOVNHK3VxSlVFR29tSjNyaGJadzdJdlo3T0VSQXN2eE9rbCs4MVNjcQo3elIrb0pEN0RzTFcvOFBvRXlsMnc4b1"
    "dyWkNWZTRjNFNUL2dKOGxlVDlBbkNBcnN1QVpDR2JJZ3B2MnRDKzVyCnAwZTRkR3JGdlRoNVpaVmx6b2pvOW1JdmNTZHlZRGFiY"
    "0dMZTEzNmgwU1VjNDNYbDJrTXlaRDUrN2ZoelNMMkMKVjhQM282eE0rb1c1NlJ3QjE5S1BPcVZ3Uit0eVBTVE1MMXpaTGw5bmkv"
    "bW1ndk1uTTQrTlpkMFliaXZ3Zy9GaAp6RkRrT2dwVEtmNWNvU2Z1SUpPYmtieTNNZ2MzM3NWQm1JZ2dXNnFjR2tzNFlEVC9SSEY"
    "1ZUZFNm52YVZTMy9pCnpOTmY0eFQvZTQ5dHRweG9MSTZNc0Fub2ZpQ0YwS0d4b1FiNUU0YnlndXRieS94NUh3NmJNNm9PeDZzQ0"
    "F3RUEKQVFLQ0FnQWtkSnhHdzk0aFZqVkJ2Nng5eHF0SmJYQXdld0FyeVExY2QwaVlodUZPUlFLK0hxTzdKL0JnOTJMNgorSkFPO"
    "UdNL01JSVFnSDI3LzFDVmhIaFJvNXl5Q0RkTWlRMzBSaGY4YW9sT1l4bUlydGxVY0dQc3BRVVpUZkhZCmVyZTI0NHRxZE9CVjVh"
    "VWJ1MWVlbE9HRDdMbGF3d2JHd0xoMnl5UlJRb3NHemlOQnhEOXRrQWl1RE1LL2xacVUKS3Q0ajExM0VDaG5nMmZOWm82MUYyQ0U"
    "4dWo4dktReHplZExnTG1tNFBQYzJIMFU4TWlVTGh3emRMaWF4NlpTNgpFb3FzNVlDb2VXVGIzV0l2My9KNklaM2JuU0RnU1ZBUl"
    "ZuNGp0V2hXVjNlNWZTQ2dWU3JJdE8xTHkwTVNxQ3h1CnFTSnhIT2NBd1hSaHQ5T1lTQUdhSldHUDZRK2tMMmRSOEJTdTVoU1U4Z"
    "VR3VDhCTitaRlNXWmlLWXdPNlkrTkYKbXZLemN2cUFJUEtYRFhUYTlWZjVPcG41Q0t4SHpmU3ozalViemtNZ1lBNzFRMWFxYzZQ"
    "T2xaYnI0dWxJd2pPdApRWDdvV0o2K2Y5QUdQUFdwQ3pnNFpMWXFUeE12dVBTYi9ia2Ixcks5U1NIUVB1OElEb1I1M1E4OUN0VVZ"
    "WWnhRCnlyY2xCUkR4ZFNjeEo4bWw2ajBzRVY4V2FjK1FhTG1xM0E2cDJZeHhmMnZDUVhybGFnb3RnZnRxdW9mcUZZWSsKWEdkOE"
    "dVN0pSaFZZNDZwbzhhYSt1dHptV0tobERYSHdnODBvZFhnR0RQbjlUK2d1QUZ2MWJlNXpJeFhNWWZ5eApWQ2x4WlJTRk9HeENOT"
    "kZjVEVGODdSSGRiMGtMR0t0MTFMdWpNWUNyVmJ0UW5WSXlxUUtDQVFFQTRlUGp0bStRCjBmK290emFYTnpkaGU4ZFNoL1NicytX"
    "YVhOK0xvK1BCOVdPYVY0andaWVVjSFlDZEFGKzhrdTdCQXN4dlBHTnIKMmExVkJXSmFHN1dVNktVaW1xaG1pcUNNbmpSdzVoazh"
    "LeHNrY0xJM2laRFZINm5aR0hPQlZuSkphWDgrZ2c3Sgo4a0o3VXY4SHhQY0g0VDJvSVphUWlkUEtsQXpxUVR2MTM3YUVweTZ4Tj"
    "RlenlZUGpsYzU2bWYyL2VDU25STktMClNsZWpQN2lsWWhFQ3FXalh2UmVrOCtKYU55S2JSOFQ2TC9kenRsZWc2NHlPMTkyUks3S"
    "XF4WlFIZ3luZllqN1MKdGkxME8xUjFCdm5sOVFMOGN2OWYwYkltc00xTU52dDRZazJMajdEalZhLytmTlAxNlBONHd2UlFXOVc0"
    "RzBwWApyUmxZQjYzaUh1WUJvd0tDQVFFQXZXZlp5M1d2alI0dUwrQm9HU054M0t5WnNwQkFDMnFiN1pNd2ovT1F6QUNZCjlOWVN"
    "ObHYvcXdiSWxGZy9SRXNqTko4bWFQY013MEFsTlovTmxnc2Y3L0I1bzNZQ0lKT2xGWVpiZGEyRVhqcXIKc2tGNHFEZC9LQVYrSH"
    "RGSmJ2cTEwVGtWY216Q1F5SVR5bkM5L3UzMnpvRGxUWEJFU3grT1h3bHR4YkEvcmd0NQpkRmJuNlRCWlphN3pjcWlCUlBCNGlwK"
    "0w1ZHZrckdWalQrZzBtVmdVQ212USs5OXBNN2Z1Wk56NzhGYXhIZmRCCmU2RlpFUkxxcStwaHhWNkUzQ0pOWHJOZXhtSUgzWmk1"
    "SHBZVHZYcnppWEF1TVE0aWNDbGN6Y0xCNHhlT3F3Z2QKcVVjbExQK0tmVXVpUDZMMGtvUjl6SXBzWWIrSEhGU2gvdUkrejBaU1d"
    "RS0NBUUFZQU5OTnE0VkVDMXF1UFVyTQpQMEpJbU9HWU9OSGl4OThqUjAzYldIUmYwdm12bTRtUUFCa0F1WTMxWURiMWxoRkVidH"
    "pUR2UxMzhBYzh6enFyCi94dVhyUlNFUXFqQ3lsU202d09rTDhKSkFsVlk5RmNhY3gxeWcrWGh4MFJUSDBuVndBT3daa25uU0ZFN"
    "mZJY2kKMHUwdmJoSFRuK0EwQlNGZG9oR3laT0MzcVBsbm1ucVNZQVVtd0xFS1ZpcUkrb0hDRG9NSHVTZTcrcHdLUldDdApqd2t0"
    "WDBxdGVUbTZBSzk5ZEZ2endHYWxlakg5aWtvN1BYQmdWOWI1UWJGeDFVMEhEd2dCdEpOSGNJVU5XT2dtCm1aOXA3YXROdlAwOWx"
    "5U3RYT05nWkZCaWdjTDJ2ZUVxVmMxQkRuVHZFQkFoQnowU3hSOFBKMU14dmFPeERUVWQKKzJycEFvSUJBUUMydi9jekN2QkJsdm"
    "MxbHE2YVlzckFBNEdnK3ZId2tnSzFiaW1URzQyQWFLc3N3VWg5VHJNWApUOHBFNkFqVFdqUXoxOE4xejdsdXd2dWtDL2FQYVZoO"
    "WFHZlZRazIzSlA1S0VJTTZ2aHRUMkFSR1VFbWM5VDhwClhITmVSTTAzMll1SXZpMWxaRzdqMjRPQTl0czdtRnRrMEpWdTdIM1lo"
    "akFXbnNCZDJEcjVNWFVVdmEyeUg4YUMKQ0JZNWNVQ1pSZlRvdkJ4OXduZVhwNVAxUzdWRXArbGVUTDB0NlZoV1lJZ1NwZTRvN1Z"
    "5ajd5Z3RvM2FPdE5QYwo0SjlKa25OYSszWHZnOTVVUjg0VEVBSzk4a3hGck5aQ3JBekZwRCt5UFJhZ0tlUnR1eE1iRHcrZmYxZn"
    "RYUHRBCi9iTWs5NVJIc3JLMm9uRUV0NG9qMmIwY2N5dnJUb3l4QW9JQkFEamZ3WjIxZWRQL1ZCMFlIMHo0bGM5b3pUT0YKbXg5M"
    "21XTDZyNjF0NmpVT09zZTRuNE4wZERtbWJRY0h5V21FWTkvMVdDbzF6L3RBMC91OS9tQzZNYkVoQjEraApGOUFCQWRZN1dpcnVz"
    "YkJZakFldSt2NWlOMTVXYUwrVURQb0I3Wjc5S00rZVVVOWc4TUI3a3VCYmJiMm00SzUrCjlpWDdkT3hYRkRFeHQxMzh4eFAvK1p"
    "2UG1UNDBOajIrUllndHNsR25zbXNPeVk0dm0rYk82MnZMMDd3UzlObysKR0lZSjhyMVNiVUZrWnpnaWU1WkhwM28yd3J2Vy9Gaj"
    "lWWlBxbGhGQ2V4TUdYMTlybm5PZW4zcW01MlFGS0MxZgorbjZHZEVzdGdiNXVKeUtseGZqeDQwNDJBZGFORXJKUjZLNmdMZXpVK"
    "2Y0aTNCQzNrUzZpYmVhOGQ1cz0KLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0tLS0K"
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
    context, topic: str, value: EventSchema, headers: list[tuple[str, bytes]]
):
    found = False
    for call in context.producer.send_and_wait.call_args_list:
        call_args, call_kwargs = call
        found = all(
            [
                not call_args,
                call_kwargs["topic"] == topic,
                EventSchema(**json.loads(call_kwargs["value"])) == value,
                call_kwargs["headers"] == headers,
            ]
        )
        if found:
            break
    assert found, "Mock call not found"


def create_alarms_and_vitals(
    device: Device, db: Session
) -> tuple[list[VitalRange], list[DeviceAlert]]:
    vrs = []
    alerts = []
    for _ in range(3):
        vr = DeviceVitalRangeFactory.build(device_id=device.id)
        db.add(vr)
        vrs.append(vr)

    for _ in range(3):
        alert = DeviceAlertFactory.build(device_id=device.id)
        db.add(alert)
        alerts.append(alert)
    db.flush()
    return vrs, alerts
