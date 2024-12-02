from datetime import date, datetime, timedelta, timezone

import pytest
from common_schemas.dates import TimezoneFreeDatetime
from pydantic import BaseModel, ValidationError


class Foobar(BaseModel):
    value: TimezoneFreeDatetime


@pytest.mark.parametrize(
    "input, expected",
    [
        # Timezone-aware datetime objects
        (datetime(2024, 6, 27, 12, 0, 0, tzinfo=timezone.utc), datetime(2024, 6, 27, 12, 0, 0)),
        (
            datetime(2024, 6, 27, 12, 0, 0, tzinfo=timezone(offset=timedelta(hours=-7))),
            datetime(2024, 6, 27, 12, 0, 0),
        ),
        (
            datetime(2024, 6, 27, 12, 0, 0, tzinfo=timezone(offset=timedelta(hours=5, minutes=30))),
            datetime(2024, 6, 27, 12, 0, 0),
        ),
        # UTC timestamps
        (1_493_942_400, datetime(2017, 5, 5)),
        (1_493_942_400_000, datetime(2017, 5, 5)),
        # Strings and bytes
        ("2024-06-27T12:00:00Z", datetime(2024, 6, 27, 12, 0, 0)),
        (b"2024-06-27T12:00:00Z", datetime(2024, 6, 27, 12, 0, 0)),
        # Date objects
        (date(2012, 4, 9), datetime(2012, 4, 9)),
    ],
)
def test_correct_value(input, expected):
    assert Foobar(value=input).value == expected


@pytest.mark.parametrize("value", ["foo"])
def test_timezone_free_error(value):
    with pytest.raises(ValidationError) as exc_info:
        Foobar(value=value)

    assert exc_info.value.errors(include_url=False, include_context=False) == [
        {
            "type": "datetime_from_date_parsing",
            "loc": ("value",),
            "msg": "Input should be a valid datetime or date, input is too short",
            "input": value,
        }
    ]
