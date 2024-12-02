from datetime import date
from uuid import uuid4

from factory import Factory, LazyFunction
from factory.fuzzy import FuzzyDate, FuzzyText

from src.common.models import InternalAudit

START_DATE = date(year=2020, month=1, day=1)


class InternalAuditFactory(Factory):
    class Meta:
        model = InternalAudit

    entity_id = FuzzyText()
    timestamp = FuzzyDate(start_date=START_DATE)
    data = "{}"
    event_name = FuzzyText()
    event_type = FuzzyText()
    message_id = LazyFunction(uuid4)
    emitted_by = FuzzyText()
    performed_by = FuzzyText()
