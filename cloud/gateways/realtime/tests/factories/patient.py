from polyfactory.factories.pydantic_factory import ModelFactory

from src.common.clients.patient.schemas import BedSchema, PatientSchema


class BedFactory(ModelFactory):
    __model__ = BedSchema


class PatientFactory(ModelFactory):
    __model__ = PatientSchema
