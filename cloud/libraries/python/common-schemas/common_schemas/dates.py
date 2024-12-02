from datetime import date, datetime
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator


def remove_timezone(value: datetime):
    return value.replace(tzinfo=None)


TimezoneFreeDatetime = Annotated[datetime, AfterValidator(remove_timezone)]

DateISO8601 = Annotated[
    date,
    BeforeValidator(date.fromisoformat),
]
