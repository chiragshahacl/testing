from datetime import datetime

import factory

from app.common.models import AlertLog


class PhysiologicalAlertFactory(factory.Factory):
    class Meta:
        model = AlertLog

    code = factory.Faker("bothify", text="????-########", letters="ABCDE")
    patient_id = factory.Faker("uuid4")
    determination_time = factory.LazyFunction(datetime.now)
    value_number = factory.Faker("pydecimal", max_value=10000)
    value_text = factory.Faker("random_element", elements=["LO", "NO", "HI"])
    device_primary_identifier = factory.Faker("uuid4")
    device_code = factory.Faker("bothify", text="device_code_???###", letters="ABCDE")
    active = factory.Faker("boolean")
