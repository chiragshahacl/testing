import uuid
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger

from src.alarms.constants import TechnicalAlarmCodes
from src.broker import publish_alert
from src.common.schemas import AlertPayloadSchema, AlertSchema
from src.settings import settings


async def send_alarm(
    patient_primary_identifier: str,
    code: str,
    device_code: str,
    priority: str,
    active: bool,
    determination_time: Optional[float] = None,
    device_primary_identifier: Optional[str] = None,
    alarm_range: Optional[dict] = None,
    latching: Optional[bool] = False,
):
    now = datetime.now()
    effective_determination_time = determination_time
    if determination_time is None:
        effective_determination_time = now - timedelta(milliseconds=50)

    message_payload = AlertPayloadSchema(
        patient_primary_identifier=patient_primary_identifier,
        device_primary_identifier=device_primary_identifier,
        device_code=device_code,
        code=code,
        priority=priority,
        determination_time=effective_determination_time.strftime(settings.TIMESTAMP_FORMAT),
        active=active,
        vital_range=alarm_range,
        latching=bool(latching),
    )
    message_wrapper = AlertSchema(
        message_id=str(uuid.uuid4()),
        timestamp=datetime.now().strftime(settings.TIMESTAMP_FORMAT),
        payload=message_payload,
    )

    alarm_data = message_wrapper.dict()
    logger.debug(alarm_data)
    is_technical_alert = code in iter(TechnicalAlarmCodes)
    return await publish_alert(alarm_data, patient_primary_identifier, is_technical_alert)
