from datetime import date
from typing import Any

from pydantic_core import SchemaValidator, core_schema


class SecretDate:
    """A date field used for storing sensitive information that you do not want to be visible
    in logging or tracebacks.

    It displays `'**/**/****'` instead of the date value on `repr()` and `str()` calls.
    The date will only be releaved on calling SecretDate.get_secret_value() or on JSON dumping
    the model using it

    ```py
    from pydantic import BaseModel, SecretDate

    class Event(BaseModel):
        date: SecretDate

    event = Event(date='2017-01-01')
    #> Event(date=SecretDate('**/**/****'))

    print(event.date)
    #> **/**/****

    event.date.get_secret_value()
    #> datetime.date(2017, 1, 1)
    ```
    """

    def __init__(self, secret_value) -> None:
        schema = core_schema.date_schema()
        validator = SchemaValidator(schema)
        self._secret_value = validator.validate_python(secret_value)

    def get_secret_value(self) -> date:
        """Get the secret value.

        Returns:
            The secret value.
        """
        return self._secret_value

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.get_secret_value() == other.get_secret_value()
        )

    def __hash__(self) -> int:
        return hash(self.get_secret_value())

    def __str__(self) -> str:
        return str(self._display())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._display()!r})"

    def _display(self) -> date:
        return "**/**/****" if self.get_secret_value() else ""

    @classmethod
    def __get_pydantic_core_schema__(cls, source: type[Any]) -> core_schema.CoreSchema:
        inner_schema = core_schema.date_schema()
        error_kind = "date_type"

        def serialize(value, info):
            if info.mode == "json":
                return str(value.get_secret_value())
            return value

        def get_json_schema(_core_schema, handler):
            json_schema = handler(inner_schema)
            return json_schema

        json_schema = core_schema.no_info_after_validator_function(
            source,  # construct the type
            inner_schema,
        )
        schema = core_schema.json_or_python_schema(
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(source),
                    json_schema,
                ],
                strict=False,
                custom_error_type=error_kind,
            ),
            json_schema=json_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize,
                info_arg=True,
                return_schema=core_schema.str_schema(),
                when_used="json",
            ),
        )
        schema.setdefault("metadata", {}).setdefault("pydantic_js_functions", []).append(
            get_json_schema
        )
        return schema
