from uuid import UUID

from cache import add_cache
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.requests import Request

from app.patient import schemas as patient_schemas
from app.patient.services import PatientService
from app.settings import config

api = APIRouter(prefix=config.BASE_PATH)


@api.get(
    "",
    responses={
        status.HTTP_200_OK: {"model": patient_schemas.PatientResources},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
    },
    operation_id="get-patient-list",
)
@add_cache("Patient")
async def get_patient_list(
    request: Request,  # pylint: disable=unused-argument
    patient_service: PatientService = Depends(),
    params: patient_schemas.PatientQueryParams = Depends(),
) -> patient_schemas.PatientResources:
    patients = await patient_service.get_patients(params)
    return patients


@api.get(
    "/count",
    responses={
        status.HTTP_200_OK: {"model": patient_schemas.PatientCount},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
    },
    operation_id="get-patient-count",
)
@add_cache("Patient")
async def get_patient_count(
    request: Request,  # pylint: disable=unused-argument
    patient_service: PatientService = Depends(),
    params: patient_schemas.PatientQueryParams = Depends(),
) -> patient_schemas.PatientCount:
    patient_count = await patient_service.get_patients_count(params)
    return patient_count


@api.get(
    "/{patient_id:uuid}",
    responses={
        status.HTTP_200_OK: {"model": patient_schemas.PatientSchema},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    operation_id="get-patient",
)
@add_cache("Patient")
async def get_patient_by_id(
    request: Request,  # pylint: disable=unused-argument
    patient_id: UUID,
    patient_service: PatientService = Depends(),
) -> patient_schemas.PatientSchema:
    patient = await patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return patient


@api.get(
    "/identifier/{identifier_id}",
    responses={
        status.HTTP_200_OK: {"model": patient_schemas.PatientSchema},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    operation_id="get-patient-by-identifier",
)
@add_cache("Patient")
async def get_patient_by_identifier(
    request: Request,  # pylint: disable=unused-argument
    identifier_id: str,
    patient_service: PatientService = Depends(),
) -> patient_schemas.PatientSchema:
    patient = await patient_service.get_patient_by_identifier(identifier_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return patient


@api.get(
    "/observation",
    responses={
        status.HTTP_200_OK: {"model": patient_schemas.PatientObservationResources},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
        status.HTTP_404_NOT_FOUND: {},
    },
    operation_id="get-patient-observations",
)
@add_cache("Observation")
async def get_patient_observations(
    request: Request,  # pylint: disable=unused-argument
    params: patient_schemas.PatientObservationsQueryParams = Depends(),
    patient_service: PatientService = Depends(),
) -> patient_schemas.PatientObservationResources:
    patient_observations = await patient_service.get_patient_observations(params)
    return patient_observations


@api.get(
    "/{patient_id:uuid}/session/alerts",
    responses={
        status.HTTP_200_OK: {"model": list[patient_schemas.SessionPhysiologicalAlert]},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
    },
    operation_id="get-physiological-alerts",
)
@add_cache("observation-audit")
async def get_physiological_alerts(
    request: Request,  # pylint: disable=unused-argument
    patient_id: UUID,
    patient_service: PatientService = Depends(),
) -> list[patient_schemas.SessionPhysiologicalAlert]:
    return await patient_service.get_physiological_alerts(patient_id)
