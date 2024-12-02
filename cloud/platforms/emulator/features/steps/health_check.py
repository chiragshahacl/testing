from behave import then, when
from fastapi import status


@when("I make a health check request to the app")
@when("I make a health check request to the app under `{path}`")
def step_impl(context, path: str = "/emulator/health"):
    context.response = context.client.get(path)


@then("I'm told the app is working")
def step_impl(context):
    assert context.response.status_code == status.HTTP_200_OK, context.response.status_code
    assert context.response.json() == {"status": "Healthy"}


@then("I'm told there is a problem")
def step_impl(context):
    assert context.exception
