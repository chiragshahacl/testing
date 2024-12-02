import json
from datetime import date

import pytest
from common_schemas.dates import DateISO8601
from pydantic import BaseModel, ValidationError


class Foobar(BaseModel):
    value: DateISO8601


@pytest.mark.parametrize(
    "input, expected",
    [
        # Date objects
        ("20200101", date(2020, 1, 1)),
        ("2020-01-01", date(2020, 1, 1)),
    ],
)
def test_correct_value(input, expected):
    assert Foobar(value=input).value == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        # Date objects
        ("20200101", "2020-01-01"),
        ("2020-01-01", "2020-01-01"),
    ],
)
def test_correct_serializing(input, expected):
    instance = Foobar(value=input)
    assert json.loads(instance.model_dump_json())["value"] == expected


@pytest.mark.parametrize("value", ["foo"])
def test_timezone_free_error(value):
    with pytest.raises(ValidationError) as exc_info:
        Foobar(value=value)

    assert exc_info.value.errors(include_url=False, include_context=False) == [
        {
            "type": "value_error",
            "loc": ("value",),
            "msg": "Value error, Invalid isoformat string: 'foo'",
            "input": value,
        }
    ]
