from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.responses import Response

from src.common.schemas import UpdatePatientMonitorConfigPayload
from src.emulator.memory_registry import DataManager
from src.emulator.models import Config, Patient, PatientMonitor, Sensor
from src.monitor.schemas import (
    DeviceMonitorSchema,
    DisconnectMonitorSchema,
    PatientSessionClosedPayload,
    PatientSessionOpenedPayload,
)

api = APIRouter()


@api.post(
    "/monitor/ConnectPatientMonitor",
    operation_id="connect-patient-monitor",
)
async def connect_emulated_patient_monitor(
    payload: DeviceMonitorSchema,
) -> Response:
    monitor_config = Config(
        audio_pause_enabled=payload.config.audio_pause_enabled,
        audio_enabled=payload.config.audio_enabled,
    )

    monitor = PatientMonitor(  # pylint: disable=E1120
        primary_identifier=payload.primary_identifier,
        name=payload.name,
        config=monitor_config,
    )

    if payload.patient:
        patient = Patient(
            primary_identifier=payload.patient.primary_identifier,
            birth_date=payload.patient.birth_date,
            given_name=payload.patient.given_name,
            family_name=payload.patient.family_name,
            gender=payload.patient.gender,
        )
        monitor.patient = patient

    try:
        if payload.connected_sensors:
            for connected_sensor in payload.connected_sensors:
                sensor = Sensor(
                    primary_identifier=connected_sensor.primary_identifier,
                    name=connected_sensor.name,
                    device_code=connected_sensor.device_code,
                    patient=monitor.patient,
                )
                monitor.add_sensor(sensor)

        data_manager = DataManager()
        await data_manager.connect_patient_monitor(monitor)

    except (ValueError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/monitor/DisconnectMonitor",
    operation_id="disconnect-monitor",
)
async def disconnect_emulated_monitor(
    payload: DisconnectMonitorSchema,
) -> Response:
    data_manager = DataManager()

    try:
        data_manager.disconnect_patient_monitor(
            payload.primary_identifier,
        )
    except (KeyError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/monitor/OpenPatientSession",
    operation_id="open-patient-session",
)
async def open_patient_session(
    payload: PatientSessionOpenedPayload,
) -> Response:
    data_manager = DataManager()

    patient = Patient(
        primary_identifier=payload.patient.primary_identifier,
        given_name=payload.patient.given_name,
        family_name=payload.patient.family_name,
        birth_date=payload.patient.birth_date,
        gender=payload.patient.gender,
    )

    try:
        await data_manager.open_patient_session(payload.patient_monitor_primary_identifier, patient)
    except (KeyError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/monitor/ClosePatientSession",
    operation_id="close-patient-session",
)
async def close_patient_session(
    payload: PatientSessionClosedPayload,
) -> Response:
    data_manager = DataManager()

    try:
        await data_manager.close_patient_session(payload.patient_monitor_primary_identifier)
    except (KeyError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post("/monitor/UpdatePatientMonitorConfig")
async def post_patient_monitor_configuration(
    payload: UpdatePatientMonitorConfigPayload,
) -> Response:
    data_manager = DataManager()

    config = Config(
        audio_enabled=payload.audio_enabled, audio_pause_enabled=payload.audio_pause_enabled
    )
    await data_manager.change_patient_monitor_config(payload.device_primary_identifier, config)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
