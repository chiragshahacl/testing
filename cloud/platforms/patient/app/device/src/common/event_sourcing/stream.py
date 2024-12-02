from app.common.event_sourcing.stream import BaseEventStream
from app.device.src.common.models import Device, DeviceAlert, DeviceVitalRange


class DeviceEventStream(BaseEventStream[Device]):
    pass


class VitalRangeEventStream(BaseEventStream[DeviceVitalRange]):
    pass


class AlertStream(BaseEventStream[DeviceAlert]):
    pass
