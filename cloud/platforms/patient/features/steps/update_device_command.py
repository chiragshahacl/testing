from behave import step, when


@step("a request to update a device")
def step_impl(context):
    context.device_id = "91e6c14f-1142-49c8-9898-971b726b9684"
    context.device_name = "device"
    context.device_primary_identifier = "primary-identifier"
    context.model_number = "12345-declan-walsh"
    context.request = {
        "url": "/device/UpdateDevice",
        "json": {
            "id": context.device_id,
            "name": context.device_name,
            "primary_identifier": context.device_primary_identifier,
            "model_number": context.model_number,
            "audio_pause_enabled": False,
            "audio_enabled": True,
        },
    }


@when("the request is made to update a device")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("a new name is provided")
def step_impl(context):
    context.device_name = "new-device"
    context.request["json"]["name"] = context.device_name
