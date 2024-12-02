from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.device.src.common.models import Device, DeviceAlert, DeviceVitalRange


class DeviceVitalRangeFactory(SQLAlchemyFactory[DeviceVitalRange]):
    pass


class DeviceAlertFactory(SQLAlchemyFactory[DeviceAlert]):
    priority = "LO"


class DeviceFactory(SQLAlchemyFactory[Device]):
    subject_identifier = None
    gateway_id = None
    location_id = None
    audio_pause_enabled = True
    audio_enabled = False
