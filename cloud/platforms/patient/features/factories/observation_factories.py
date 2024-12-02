from datetime import datetime

import factory

from app.common.models import Observation
from features.factories.common import Session


class ObservationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Observation
        sqlalchemy_session = Session

    id = factory.Faker("uuid4")
    category = factory.Faker(
        "random_element",
        elements=[
            "vital-signs",
        ],
    )
    code = factory.Faker("bothify", text="????-########", letters="ABCDE")
    subject_id = factory.Faker("uuid4")
    effective_dt = factory.LazyFunction(datetime.now)
    value_number = factory.Faker("pydecimal", max_value=10000)
    value_text = factory.Faker("random_element", elements=["LO", "NO", "HI"])
    device_code = factory.Faker("bothify", text="device_code_???###", letters="ABCDE")
    device_primary_identifier = factory.Faker("uuid4")
    is_alert = factory.Faker("boolean")
