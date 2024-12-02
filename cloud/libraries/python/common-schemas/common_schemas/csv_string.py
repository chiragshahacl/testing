from pydantic import AfterValidator
from typing_extensions import Annotated

CsvString = Annotated[str, AfterValidator(lambda v: [item.strip() for item in v.split(",")])]
