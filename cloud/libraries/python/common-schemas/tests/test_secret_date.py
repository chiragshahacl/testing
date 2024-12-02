from datetime import date, datetime

import pytest
from common_schemas.secret_date import SecretDate
from pydantic import BaseModel, ValidationError


class Foobar(BaseModel):
    value: SecretDate


@pytest.mark.parametrize(
    "value, result",
    [
        (1_493_942_400, date(2017, 5, 5)),
        (1_493_942_400_000, date(2017, 5, 5)),
        (0, date(1970, 1, 1)),
        ("2012-04-23", date(2012, 4, 23)),
        (b"2012-04-23", date(2012, 4, 23)),
        (date(2012, 4, 9), date(2012, 4, 9)),
        (datetime(2012, 4, 9, 0, 0), date(2012, 4, 9)),
    ],
)
def test_secretdate(value, result):
    f = Foobar(value=value)

    # Assert correct type.
    assert f.value.__class__.__name__ == "SecretDate"

    # Assert str and repr are correct.
    assert str(f.value) == "**/**/****"
    assert repr(f.value) == "SecretDate('**/**/****')"

    # Assert retrieval of secret value is correct
    assert f.value.get_secret_value() == result


def test_secretdate_equality():
    assert SecretDate("2017-01-01") == SecretDate("2017-01-01")
    assert SecretDate(date(2017, 1, 1)) == SecretDate("2017-01-01")
    assert SecretDate("2017-01-01") != SecretDate("2018-01-01")
    assert SecretDate("2017-01-01") != date(2017, 1, 1)
    assert SecretDate("2017-01-01") is not SecretDate("2017-01-01")


def test_secretdate_keeps_secrets():
    instance = Foobar(value="2017-01-01")

    assert "2017-01-01" not in instance.model_dump().values()
    assert "2017-01-01" not in str(instance)
    assert "2017-01-01" not in repr(instance)


def test_secretdate_reveals_secrets():
    instance = Foobar(value="2017-01-01")

    assert "2017-01-01" in instance.model_dump_json()


def test_secretdate_idempotent():
    # Should not raise an exception
    m = Foobar(value=SecretDate("2017-01-01"))
    assert m.value.get_secret_value() == date(2017, 1, 1)


@pytest.mark.parametrize("value", ["foo", 1, True, "2000", []])
def test_secretdate_error(value):
    with pytest.raises(ValidationError) as exc_info:
        Foobar(value=value)

    assert exc_info.value.errors(include_url=False) == [
        {
            "type": "date_type",
            "loc": ("value",),
            "msg": "Input should be a valid date",
            "input": value,
        }
    ]


def test_secretdate_as_list():
    class DateList(BaseModel):
        value: list[SecretDate]

    result = DateList(value=["2017-01-01", "2018-01-01", "2019-01-01"])

    assert [x.get_secret_value() for x in result.value] == [
        date(2017, 1, 1),
        date(2018, 1, 1),
        date(2019, 1, 1),
    ]


def test_secretdate_is_hashable():
    m = Foobar(value=SecretDate("2017-01-01"))
    hash(m.value)
