from behave import *


@when("I make a health check request to the app")
def step_impl(context):
    context.response = context.client.get("/health")


@then("I'm told the app is working")
def step_impl(context):
    assert context.response.status_code == 200
    assert context.response.json() == {"status": "Healthy"}
