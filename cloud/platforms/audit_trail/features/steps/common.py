import base64
import datetime

import jwt
from behave import *
from starlette import status

VALID_PRIVATE_KEY = """
LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlKS0FJQkFBS0NBZ0VBcHlEaC9BSllFdXFuMlRGVXhqazc5eno2V1VGcmJ3Rk5DaFdyWWUvY3ROK3ZpdnJVCnVPakt6YXFHZ3VwT0tKclZlSE8wMTJkM1ZrRGozM1p1QzROd2xxZjYvOUY4QnFCd3BoWHVsNkhOelB6YmdBL28KbUdBN1I4aXZpZ2l3VC8rY2lseEJ4V004WFdFRmZNTmdCdGhVbGtDeFB5MnRkRjNJNTdTbVBtUzdhNjNsZ3RWTgpxSXZvMVdVVlIzeVpPelA4OGU1Y0FsTXZYaGkvTmMrZFlTckZZdVpON1FwbTJCMmVIQzVmQlI4TXFRQ0lWL2JvCjdoVmx3d2R6dll5WkdkN3p4dzNwVERGYXliSjcxVmh2Nk5oVmpYdkIrckVDTW9KMWFxRExjdkFwcE1yT29wUkMKRjZxR0pUZDRobWhlUENQc3kvb3V0TnFhOVNHK3VxSlVFR29tSjNyaGJadzdJdlo3T0VSQXN2eE9rbCs4MVNjcQo3elIrb0pEN0RzTFcvOFBvRXlsMnc4b1dyWkNWZTRjNFNUL2dKOGxlVDlBbkNBcnN1QVpDR2JJZ3B2MnRDKzVyCnAwZTRkR3JGdlRoNVpaVmx6b2pvOW1JdmNTZHlZRGFiY0dMZTEzNmgwU1VjNDNYbDJrTXlaRDUrN2ZoelNMMkMKVjhQM282eE0rb1c1NlJ3QjE5S1BPcVZ3Uit0eVBTVE1MMXpaTGw5bmkvbW1ndk1uTTQrTlpkMFliaXZ3Zy9GaAp6RkRrT2dwVEtmNWNvU2Z1SUpPYmtieTNNZ2MzM3NWQm1JZ2dXNnFjR2tzNFlEVC9SSEY1ZUZFNm52YVZTMy9pCnpOTmY0eFQvZTQ5dHRweG9MSTZNc0Fub2ZpQ0YwS0d4b1FiNUU0YnlndXRieS94NUh3NmJNNm9PeDZzQ0F3RUEKQVFLQ0FnQWtkSnhHdzk0aFZqVkJ2Nng5eHF0SmJYQXdld0FyeVExY2QwaVlodUZPUlFLK0hxTzdKL0JnOTJMNgorSkFPOUdNL01JSVFnSDI3LzFDVmhIaFJvNXl5Q0RkTWlRMzBSaGY4YW9sT1l4bUlydGxVY0dQc3BRVVpUZkhZCmVyZTI0NHRxZE9CVjVhVWJ1MWVlbE9HRDdMbGF3d2JHd0xoMnl5UlJRb3NHemlOQnhEOXRrQWl1RE1LL2xacVUKS3Q0ajExM0VDaG5nMmZOWm82MUYyQ0U4dWo4dktReHplZExnTG1tNFBQYzJIMFU4TWlVTGh3emRMaWF4NlpTNgpFb3FzNVlDb2VXVGIzV0l2My9KNklaM2JuU0RnU1ZBUlZuNGp0V2hXVjNlNWZTQ2dWU3JJdE8xTHkwTVNxQ3h1CnFTSnhIT2NBd1hSaHQ5T1lTQUdhSldHUDZRK2tMMmRSOEJTdTVoU1U4ZVR3VDhCTitaRlNXWmlLWXdPNlkrTkYKbXZLemN2cUFJUEtYRFhUYTlWZjVPcG41Q0t4SHpmU3ozalViemtNZ1lBNzFRMWFxYzZQT2xaYnI0dWxJd2pPdApRWDdvV0o2K2Y5QUdQUFdwQ3pnNFpMWXFUeE12dVBTYi9ia2Ixcks5U1NIUVB1OElEb1I1M1E4OUN0VVZWWnhRCnlyY2xCUkR4ZFNjeEo4bWw2ajBzRVY4V2FjK1FhTG1xM0E2cDJZeHhmMnZDUVhybGFnb3RnZnRxdW9mcUZZWSsKWEdkOEdVN0pSaFZZNDZwbzhhYSt1dHptV0tobERYSHdnODBvZFhnR0RQbjlUK2d1QUZ2MWJlNXpJeFhNWWZ5eApWQ2x4WlJTRk9HeENOTkZjVEVGODdSSGRiMGtMR0t0MTFMdWpNWUNyVmJ0UW5WSXlxUUtDQVFFQTRlUGp0bStRCjBmK290emFYTnpkaGU4ZFNoL1NicytXYVhOK0xvK1BCOVdPYVY0andaWVVjSFlDZEFGKzhrdTdCQXN4dlBHTnIKMmExVkJXSmFHN1dVNktVaW1xaG1pcUNNbmpSdzVoazhLeHNrY0xJM2laRFZINm5aR0hPQlZuSkphWDgrZ2c3Sgo4a0o3VXY4SHhQY0g0VDJvSVphUWlkUEtsQXpxUVR2MTM3YUVweTZ4TjRlenlZUGpsYzU2bWYyL2VDU25STktMClNsZWpQN2lsWWhFQ3FXalh2UmVrOCtKYU55S2JSOFQ2TC9kenRsZWc2NHlPMTkyUks3SXF4WlFIZ3luZllqN1MKdGkxME8xUjFCdm5sOVFMOGN2OWYwYkltc00xTU52dDRZazJMajdEalZhLytmTlAxNlBONHd2UlFXOVc0RzBwWApyUmxZQjYzaUh1WUJvd0tDQVFFQXZXZlp5M1d2alI0dUwrQm9HU054M0t5WnNwQkFDMnFiN1pNd2ovT1F6QUNZCjlOWVNObHYvcXdiSWxGZy9SRXNqTko4bWFQY013MEFsTlovTmxnc2Y3L0I1bzNZQ0lKT2xGWVpiZGEyRVhqcXIKc2tGNHFEZC9LQVYrSHRGSmJ2cTEwVGtWY216Q1F5SVR5bkM5L3UzMnpvRGxUWEJFU3grT1h3bHR4YkEvcmd0NQpkRmJuNlRCWlphN3pjcWlCUlBCNGlwK0w1ZHZrckdWalQrZzBtVmdVQ212USs5OXBNN2Z1Wk56NzhGYXhIZmRCCmU2RlpFUkxxcStwaHhWNkUzQ0pOWHJOZXhtSUgzWmk1SHBZVHZYcnppWEF1TVE0aWNDbGN6Y0xCNHhlT3F3Z2QKcVVjbExQK0tmVXVpUDZMMGtvUjl6SXBzWWIrSEhGU2gvdUkrejBaU1dRS0NBUUFZQU5OTnE0VkVDMXF1UFVyTQpQMEpJbU9HWU9OSGl4OThqUjAzYldIUmYwdm12bTRtUUFCa0F1WTMxWURiMWxoRkVidHpUR2UxMzhBYzh6enFyCi94dVhyUlNFUXFqQ3lsU202d09rTDhKSkFsVlk5RmNhY3gxeWcrWGh4MFJUSDBuVndBT3daa25uU0ZFNmZJY2kKMHUwdmJoSFRuK0EwQlNGZG9oR3laT0MzcVBsbm1ucVNZQVVtd0xFS1ZpcUkrb0hDRG9NSHVTZTcrcHdLUldDdApqd2t0WDBxdGVUbTZBSzk5ZEZ2endHYWxlakg5aWtvN1BYQmdWOWI1UWJGeDFVMEhEd2dCdEpOSGNJVU5XT2dtCm1aOXA3YXROdlAwOWx5U3RYT05nWkZCaWdjTDJ2ZUVxVmMxQkRuVHZFQkFoQnowU3hSOFBKMU14dmFPeERUVWQKKzJycEFvSUJBUUMydi9jekN2QkJsdmMxbHE2YVlzckFBNEdnK3ZId2tnSzFiaW1URzQyQWFLc3N3VWg5VHJNWApUOHBFNkFqVFdqUXoxOE4xejdsdXd2dWtDL2FQYVZoOWFHZlZRazIzSlA1S0VJTTZ2aHRUMkFSR1VFbWM5VDhwClhITmVSTTAzMll1SXZpMWxaRzdqMjRPQTl0czdtRnRrMEpWdTdIM1loakFXbnNCZDJEcjVNWFVVdmEyeUg4YUMKQ0JZNWNVQ1pSZlRvdkJ4OXduZVhwNVAxUzdWRXArbGVUTDB0NlZoV1lJZ1NwZTRvN1Z5ajd5Z3RvM2FPdE5QYwo0SjlKa25OYSszWHZnOTVVUjg0VEVBSzk4a3hGck5aQ3JBekZwRCt5UFJhZ0tlUnR1eE1iRHcrZmYxZnRYUHRBCi9iTWs5NVJIc3JLMm9uRUV0NG9qMmIwY2N5dnJUb3l4QW9JQkFEamZ3WjIxZWRQL1ZCMFlIMHo0bGM5b3pUT0YKbXg5M21XTDZyNjF0NmpVT09zZTRuNE4wZERtbWJRY0h5V21FWTkvMVdDbzF6L3RBMC91OS9tQzZNYkVoQjEraApGOUFCQWRZN1dpcnVzYkJZakFldSt2NWlOMTVXYUwrVURQb0I3Wjc5S00rZVVVOWc4TUI3a3VCYmJiMm00SzUrCjlpWDdkT3hYRkRFeHQxMzh4eFAvK1p2UG1UNDBOajIrUllndHNsR25zbXNPeVk0dm0rYk82MnZMMDd3UzlObysKR0lZSjhyMVNiVUZrWnpnaWU1WkhwM28yd3J2Vy9GajlWWlBxbGhGQ2V4TUdYMTlybm5PZW4zcW01MlFGS0MxZgorbjZHZEVzdGdiNXVKeUtseGZqeDQwNDJBZGFORXJKUjZLNmdMZXpVK2Y0aTNCQzNrUzZpYmVhOGQ1cz0KLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0tLS0K
"""


def generate_valid_jwt_token(context) -> str:
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
    valid_key = base64.b64decode(VALID_PRIVATE_KEY).decode("utf-8")
    token = jwt.encode(token, key=valid_key, algorithm="RS256")
    return f"Bearer {token}"


def generate_invalid_jwt_token(context) -> str:
    now = datetime.datetime.now()
    exp = now + datetime.timedelta(days=1)
    token = {
        "token_type": "access",
        "exp": exp.timestamp(),
        "iat": now.timestamp(),
        "aud": "tucana",
    }
    valid_key = base64.b64decode(VALID_PRIVATE_KEY).decode("utf-8")
    token = jwt.encode(token, key=valid_key, algorithm="RS256")
    return f"Bearer {token}"


@given("the application is running")
def step_impl(context):
    pass


@step("the user is told the request was successful")
def step_impl(context):
    assert (
        status.HTTP_204_NO_CONTENT >= context.response.status_code >= status.HTTP_200_OK
    ), context.response.status_code


@step("the user is told the requested resource was not found")
def step_impl(context):
    assert context.response.status_code == status.HTTP_404_NOT_FOUND, context.response.status_code


@step("valid authentication credentials are being included")
def step_impl(context):
    context.internal_token = generate_valid_jwt_token(context)
    context.request["headers"] = {"Authorization": context.internal_token}


@step("invalid authentication credentials are being included")
def step_impl(context):
    context.internal_token = generate_invalid_jwt_token(context)
    context.request["headers"] = {"Authorization": context.internal_token}


@step("the user is told the request was unauthorized")
def step_impl(context):
    assert (
        context.response.status_code == status.HTTP_401_UNAUTHORIZED
    ), context.response.status_code


@step("the user is told the request was forbidden")
def step_impl(context):
    assert context.response.status_code == status.HTTP_403_FORBIDDEN, context.response.status_code
