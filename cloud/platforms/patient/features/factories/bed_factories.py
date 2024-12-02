import factory
from factory.faker import Faker as FactoryFaker
from faker import Faker

from app.common.models import Bed
from features.factories.common import Session


class BedFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Bed
        sqlalchemy_session = Session

    id = FactoryFaker("uuid4")
    name = factory.Sequence(lambda n: str(Faker().uuid4()))
