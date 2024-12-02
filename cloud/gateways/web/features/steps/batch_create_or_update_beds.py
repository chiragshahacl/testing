import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to batch create or update beds")
def step_impl(context):
    context.payload = [
        {"id": "f4cdb911-3049-45c3-9cc1-68a63790115f", "name": "bed1"},
        {"id": "4fa1286a-5019-4a6c-8b51-affcfbcb8b22", "name": "bed2"},
        {"id": "cb3dbec8-9720-40e0-bfab-6e53bfa5978d", "name": "bed3"},
        {"id": "2c93e058-5374-4aec-ae78-498b378850c4", "name": "bed4"},
        {"name": "createMe"},
    ]

    context.request = {
        "url": "/web/bed/batch",
        "json": {
            "resources": context.payload,
        },
    }


@step("a request to batch create or update beds 2")
def step_impl(context):
    context.payload = [
        {"id": "f4cdb911-3049-45c3-9cc1-68a63790115f", "name": "bed1"},
        {"id": "4fa1286a-5019-4a6c-8b51-affcfbcb8b22", "name": "bed2"},
        {"name": "createMe1"},
        {"name": "createMe2"},
        {"name": "createMe3"},
    ]

    context.request = {
        "url": "/web/bed/batch",
        "json": {
            "resources": context.payload,
        },
    }


@when("the request is made to batch create or update some beds")
def step_impl(context):
    context.response = context.client.put(**context.request)


@step("the beds can be created or updated")
def step_impl(context):
    context.get_beds = [
        {
            "id": "f4cdb911-3049-45c3-9cc1-68a63790115f",
            "name": "bed11",
            "patient": None,
        },
        {
            "id": "4fa1286a-5019-4a6c-8b51-affcfbcb8b22",
            "name": "bed21",
            "patient": None,
        },
        {
            "id": "cb3dbec8-9720-40e0-bfab-6e53bfa5978d",
            "name": "bed31",
            "patient": None,
        },
        {
            "id": "2c93e058-5374-4aec-ae78-498b378850c4",
            "name": "bed41",
            "patient": None,
        },
    ]

    context.updated_beds = [
        {"id": "f4cdb911-3049-45c3-9cc1-68a63790115f", "name": "bed1", "patient": None},
        {"id": "4fa1286a-5019-4a6c-8b51-affcfbcb8b22", "name": "bed2", "patient": None},
        {"id": "cb3dbec8-9720-40e0-bfab-6e53bfa5978d", "name": "bed3", "patient": None},
        {"id": "2c93e058-5374-4aec-ae78-498b378850c4", "name": "bed4", "patient": None},
    ]

    context.get_beds_response = respx.get(f"{settings.PATIENT_PLATFORM_BASE_URL}/bed").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "resources": context.get_beds,
            },
        )
    )
    context.batch_update_response = respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed/BatchUpdateBeds",
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "resources": context.updated_beds,
            },
        )
    )
    context.payload.append({"name": "createMe"})
    context.batch_create_response = respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed/BatchCreateBeds",
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "resources": [{"id": "0439c727-2918-463d-bbf4-0f0e8b801c9c", "name": "createMe"}],
            },
        )
    )


@step("the beds can be created or updated 2")
def step_impl(context):
    context.get_beds = [
        {
            "id": "f4cdb911-3049-45c3-9cc1-68a63790115f",
            "name": "bed1",
            "patient": None,
        },
        {
            "id": "4fa1286a-5019-4a6c-8b51-affcfbcb8b22",
            "name": "bed21",
            "patient": None,
        },
    ]

    context.updated_beds = [
        {"id": "4fa1286a-5019-4a6c-8b51-affcfbcb8b22", "name": "bed2", "patient": None},
    ]

    context.created_beds = [
        {"id": "0439c727-2918-463d-bbf4-0f0e8b801c9c", "name": "createMe1"},
        {"id": "897967a8-53df-4ef1-9abb-70e7d6556b59", "name": "createMe2"},
        {"id": "66875fab-b97a-431c-8ed7-e23ac31a04c0", "name": "createMe3"},
    ]

    context.get_beds_response = respx.get(f"{settings.PATIENT_PLATFORM_BASE_URL}/bed").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "resources": context.get_beds,
            },
        )
    )
    context.batch_update_response = respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed/BatchUpdateBeds",
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "resources": context.updated_beds,
            },
        )
    )

    context.batch_create_response = respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/bed/BatchCreateBeds",
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "resources": context.created_beds,
            },
        )
    )
