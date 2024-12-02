from behave import then, when


@when("I make a health check request to the app")
def step_impl(context):
    try:
        context.response = context.client.get("/health")
    except Exception as e:
        context.exception = e
        if not getattr(context, "expect_exception", False):
            raise e


@then("I'm told the app is working")
def step_impl(context):
    assert context.response.status_code == 200
    assert context.response.json() == {"status": "Healthy"}


@then("I'm told there is a problem")
def step_impl(context):
    assert context.exception
