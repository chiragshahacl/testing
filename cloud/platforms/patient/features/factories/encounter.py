from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.encounter.models import Encounter


class EncounterFactory(SQLAlchemyFactory[Encounter]):
    device = None
    patient = None
