"""
Pydantic's SecretStr but with secret reveal on JSON serializing
"""

from pydantic import (
    PlainSerializer,
)
from pydantic import (
    SecretStr as PydanticSecretString,
)
from typing_extensions import Annotated


class RedactedRawStringType(str):
    def __repr__(self):
        return "< redacted >"


class RedactedString(PydanticSecretString):
    def get_secret_value(self) -> RedactedRawStringType:
        value = super().get_secret_value()
        return RedactedRawStringType(value)


class RedactedDateString(RedactedString):
    pass


SecretString = Annotated[
    RedactedString,
    PlainSerializer(lambda v: v.get_secret_value() if v else None, when_used="json"),
]

SecretDateString = Annotated[
    RedactedDateString,
    PlainSerializer(lambda v: v.get_secret_value() if v else None, when_used="json"),
]
