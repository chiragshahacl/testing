from behave import step, when


@step("a valid request to get a patient by id")
def step_impl(context):
    context.patient_id = "91e6c14f-1142-49c8-9898-971b726b9684"
    context.patient_primary_identifier = "primary-identifier"
    context.patient_active = True
    context.patient_given_name = "given"
    context.patient_family_name = "family"
    context.patient_gender = "male"
    context.patient_birthdate = "2020-03-29"
    context.request = {
        "url": f"/patient/{context.patient_id}",
    }


@when("the request is made to get a patient by id")
def step_impl(context):
    context.response = context.client.get(**context.request)
