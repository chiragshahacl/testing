from common_schemas import CsvString
from pydantic import BaseModel


class FooBar(BaseModel):
    data: CsvString


def test_csv_string():
    csv_string = "value1, value2 , value 3"

    result = FooBar(data=csv_string)

    assert result.data == ["value1", "value2", "value 3"]
