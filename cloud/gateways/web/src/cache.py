import time
import uuid
from datetime import datetime

from src.device.schemas import WebDeviceAlert, WebDeviceResources

KEEP_ALIVE_THRESHOLD = 2500
MONITORS_KEEP_ALIVE_TIME: dict[str, int] = {}
MONITOR_NOT_AVAILABLE_CODE = "MonitorNotAvailable"


def monitor_keep_alive(monitor_id: str):
    MONITORS_KEEP_ALIVE_TIME[monitor_id] = time.time() * 1000


def generate_monitor_not_available_alert() -> WebDeviceAlert:
    return WebDeviceAlert(
        id=str(uuid.uuid4()),
        code=MONITOR_NOT_AVAILABLE_CODE,
        priority="HI",
        created_at=datetime.now(),
    )


def add_monitor_not_available_alerts(
    devices: list[WebDeviceResources],
) -> list[WebDeviceResources]:
    updated_devices = devices.copy()
    current_time = time.time() * 1000
    for i, device in enumerate(devices.resources):
        if not device.gateway_id:
            # It's a patient monitor
            last_keep_alive = MONITORS_KEEP_ALIVE_TIME.get(device.primary_identifier)
            if not last_keep_alive or last_keep_alive + KEEP_ALIVE_THRESHOLD < current_time:
                updated_devices.resources[i].alerts.append(generate_monitor_not_available_alert())
    return updated_devices
