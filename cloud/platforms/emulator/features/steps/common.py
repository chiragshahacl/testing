from behave import given
from behave.api.async_step import async_run_until_complete


@given("the application is running")
@async_run_until_complete
async def step_impl(context):
    pass
