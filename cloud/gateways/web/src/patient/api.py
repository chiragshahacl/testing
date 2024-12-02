from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from starlette import status

from src.common.platform.patient import schemas as patient_platform_schemas
from src.common.responses import FastJSONResponse
from src.common.schemas import base as common_schemas
from src.patient import schemas as web_patient_schemas
from src.patient import services as patient_services

api = APIRouter()


@api.post(
    "/patient",
    responses={
        status.HTTP_200_OK: {"model": patient_platform_schemas.PlatformPatient},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="create-patient",
)
async def create_patient_api(
    payload: patient_platform_schemas.CreatePatientSchema,
    patient_service: patient_services.PatientService = Depends(),
) -> FastJSONResponse:
    patient = await patient_service.create_patient(payload)
    return FastJSONResponse(patient)


@api.put(
    "/patient",
    responses={
        status.HTTP_200_OK: {"model": {}},
        status.HTTP_201_CREATED: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="upsert-patient",
)
async def upsert_patient_api(
    response: Response,
    payload: patient_platform_schemas.UpsertPatientSchema,
    patient_service: patient_services.PatientService = Depends(),
) -> Response:
    _, created = await patient_service.create_or_update_patient(payload)
    response.status_code = status.HTTP_200_OK
    if created:
        response.status_code = status.HTTP_201_CREATED
    return response


@api.get(
    "/patient",
    responses={
        status.HTTP_200_OK: {"model": web_patient_schemas.WebPatientResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="get-patient-list",
    response_class=FastJSONResponse,
)
async def get_patient_list(
    patient_service: patient_services.PatientService = Depends(),
) -> FastJSONResponse:
    patients = await patient_service.get_patients()
    return FastJSONResponse(patients)


@api.get(
    "/patient/{patient_id:uuid}",
    responses={
        status.HTTP_200_OK: {"model": web_patient_schemas.WebPatient},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_404_NOT_FOUND: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="get-patient",
    response_class=FastJSONResponse,
)
async def get_patient(
    patient_id: UUID,
    patient_service: patient_services.PatientService = Depends(),
) -> FastJSONResponse:
    patient = await patient_service.get_patient(patient_id)

    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FastJSONResponse(patient)


@api.delete(
    "/patient/{patient_id:uuid}",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="delete-patient",
)
async def delete_patient(
    patient_id: UUID,
    patient_service: patient_services.PatientService = Depends(),
) -> Response:
    await patient_service.delete_patient(patient_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.get(
    "/patient/{patient_id:uuid}/session/alerts",
    responses={
        status.HTTP_200_OK: {"model": web_patient_schemas.WebSessionAlertResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_404_NOT_FOUND: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="get-session-alerts",
    response_class=FastJSONResponse,
    response_model_by_alias=True,
)
async def get_session_alerts(
    patient_id: UUID,
    session_alert_service: patient_services.SessionAlertsService = Depends(),
) -> FastJSONResponse:
    alerts = await session_alert_service.get_session_alerts(patient_id)

    return FastJSONResponse(alerts)


@api.get(
    "/patient/ehr",
    responses={
        status.HTTP_200_OK: {"model": patient_platform_schemas.PlatformEHRPatientResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_404_NOT_FOUND: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="get-ehr-patients",
    response_class=FastJSONResponse,
    response_model_by_alias=True,
)
async def get_ehr_patients(
    patient_identifier: str = Query(default=None, alias="patientIdentifier"),
    given_name: str = Query(default=None, alias="givenName"),
    family_name: str = Query(default=None, alias="familyName"),
    birth_date: str = Query(default=None, alias="birthDate"),
    ehr_service: patient_services.EHRService = Depends(),
) -> FastJSONResponse:
    if not patient_identifier and not (family_name and given_name):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="patientIdentifier or givenName and familyName are required",
        )

    params = patient_platform_schemas.PlatformGetEHRPatientParams(
        patient_identifier=patient_identifier,
        given_name=given_name,
        family_name=family_name,
        birth_date=birth_date,
    )

    patients = await ehr_service.get_ehr_patients(params)

    return FastJSONResponse(patients)


@api.post(
    "/patient/admission",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_404_NOT_FOUND: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="patient-ehr-admission",
    response_class=FastJSONResponse,
    response_model_by_alias=True,
)
async def patient_ehr_admission(
    payload: web_patient_schemas.WebPatientAdmission,
    patient_service: patient_services.PatientService = Depends(),
) -> FastJSONResponse:
    await patient_service.encounter_patient_admission(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.delete(
    "/patient/{patient_id:uuid}/admission",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="delete-patient-admission",
)
async def delete_patient_admission(
    patient_id: UUID,
    patient_service: patient_services.PatientService = Depends(),
) -> Response:
    await patient_service.delete_patient_admission(patient_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
