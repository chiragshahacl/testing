from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import Response

from src.emulator.memory_registry import DataManager
from src.emulator.models import Sensor
from src.sensor.schemas import (
    DeviceSensorSchema,
    DisconnectSensorSchema,
    UpdateSensorModeWebSchema,
)

api = APIRouter()


@api.post(
    "/sensor/ConnectSensor",
    operation_id="connect-sensor",
)
async def connect_emulated_sensor(
    payload: DeviceSensorSchema,
) -> Response:
    data_manager = DataManager()

    sensor = Sensor(
        primary_identifier=payload.primary_identifier,
        name=payload.name,
        device_code=payload.device_code,
        patient=None,
    )
    try:
        await data_manager.connect_sensor(payload.patient_monitor_primary_identifier, sensor)
    except (KeyError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/sensor/DisconnectSensor",
    operation_id="disconnect-sensor",
)
async def disconnect_emulated_sensor(
    payload: DisconnectSensorSchema,
) -> Response:
    data_manager = DataManager()

    try:
        await data_manager.disconnect_sensor(payload.primary_identifier)
    except (KeyError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/sensor/UpdateSensorMode",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
    },
    operation_id="update-sensor-mode",
)
async def update_sensor_mode(
    payload: UpdateSensorModeWebSchema,
) -> Response:
    data_manager = DataManager()
    try:
        sensor = data_manager.get_sensor(payload.primary_identifier)
        sensor.change_mode(payload.mode, payload.emulator_name)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)
