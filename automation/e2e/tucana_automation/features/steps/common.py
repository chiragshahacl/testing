from yaml import safe_load
from httpx import Client


def parse_text(context):
    try:
        if context.text:
            return safe_load(context.text)
        return {}
    except Exception:
        raise ValueError(f"{context.text} is not a valid YAML")


def init_emulator_client(context):
    context.emulator_client = Client(
        base_url=context.env_config["api_url"] + "/emulator"
    )


def init_api_client(context):
    context.api_client = Client(
        base_url=context.api_url,
        headers={
            "Authorization": f"Bearer {context.access_token}",
        },
    )


def assert_response(response, service_name, expected_status_code=204):
    status_code = response.status_code
    assert (
        status_code == expected_status_code
    ), f"{service_name} failed with {status_code} : {response.text}"
