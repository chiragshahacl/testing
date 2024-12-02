import base64

from pydantic import AfterValidator
from typing_extensions import Annotated

Base64String = Annotated[str, AfterValidator(lambda v: base64.b64decode(v).decode("utf-8"))]
