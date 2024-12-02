from fastapi import APIRouter
from starlette import status
from starlette.responses import Response

from src.alarms.manager import send_alarm
from src.alarms.schemas import AlarmPayload, DeviceRangesPayload, TechnicalAlarmPayload
from src.broker import publish_device_ranges

api = APIRouter()


@api.put("/alarm")
async def put_alarm_api(payload: AlarmPayload) -> Response:
    await send_alarm(
        patient_primary_identifier=payload.patient_primary_identifier,
        code=payload.code.value,
        device_code=payload.device_code.value,
        device_primary_identifier=payload.device_primary_identifier,
        priority=payload.priority.value,
        active=payload.active,
        alarm_range=payload.vital_range.dict() if payload.vital_range else None,
        latching=bool(payload.latching),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.put("/technical_alert")
async def put_technical_alert(payload: TechnicalAlarmPayload) -> Response:
    await send_alarm(
        patient_primary_identifier=payload.patient_primary_identifier,
        device_primary_identifier=payload.device_primary_identifier,
        code=payload.code.value,
        device_code=payload.device_code.value,
        priority=payload.priority.value,
        active=payload.active,
        alarm_range=payload.vital_range.dict() if payload.vital_range else None,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.put("/device/range")
async def put_device_range_api(payload: DeviceRangesPayload) -> Response:
    await publish_device_ranges(payload, payload.primary_identifier)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
