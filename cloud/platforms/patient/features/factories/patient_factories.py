from datetime import date

import factory
from factory.faker import Faker as FactoryFaker
from faker import Faker

from app.common.models import Patient
from app.patient.enums import GenderEnum


class PatientFactory(factory.Factory):
    class Meta:
        model = Patient

    id = FactoryFaker("uuid4")
    primary_identifier = factory.Sequence(lambda n: Faker().uuid4())
    active = FactoryFaker("boolean")
    given_name = FactoryFaker("first_name")
    family_name = FactoryFaker("last_name")
    gender = FactoryFaker("random_element", elements=GenderEnum)
    birth_date = FactoryFaker("past_date", start_date=date(year=1990, month=1, day=1))
