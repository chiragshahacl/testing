from behave import step


@step("a valid request to get a patient by identifier")
def step_impl(context):
    context.patient_id = "91e6c14f-1142-49c8-9898-971b726b9684"
    context.patient_primary_identifier = "primary-identifier"
    context.patient_active = True
    context.patient_given_name = "given"
    context.patient_family_name = "family"
    context.patient_gender = "male"
    context.patient_birthdate = "2020-03-29"
    context.request = {
        "url": f"/patient/identifier/{context.patient_primary_identifier}",
    }


@step("the patient identifier id was provided in uppercase")
def step_impl(context):
    context.request["url"] = f"/patient/identifier/{context.patient_primary_identifier.upper()}"


@step("the request is made to get a patient by identifier")
def step_impl(context):
    context.response = context.client.get(**context.request)
