from common_schemas.secret_string import SecretString
from pydantic import BaseModel


class Foo(BaseModel):
    secret: SecretString
    non_secret: str


def test_base_schema_keeps_secrets():
    instance = Foo(secret="foo", non_secret="bar")

    assert "bar" in instance.model_dump().values()
    assert "foo" not in instance.model_dump().values()

    assert "bar" in str(instance)
    assert "foo" not in str(instance)

    assert "bar" in repr(instance)
    assert "foo" not in repr(instance)


def test_base_schema_reveals_secrets_on_json():
    instance = Foo(secret="foo", non_secret="bar")

    assert "bar" in instance.model_dump_json()
    assert "foo" in instance.model_dump_json()
