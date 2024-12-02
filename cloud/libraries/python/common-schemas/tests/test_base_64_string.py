import base64

from common_schemas.base_64_string import Base64String
from pydantic import BaseModel


class Foobar(BaseModel):
    public_key: Base64String


def test_base_64_string():
    decoded_value = "decoded"
    b64_encoded_value = base64.b64encode(decoded_value.encode())

    value = Foobar(public_key=b64_encoded_value)

    assert value.public_key == decoded_value
