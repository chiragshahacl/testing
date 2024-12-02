from cache import remove_cache
from fastapi import APIRouter, Depends, HTTPException, Response
from starlette import status

from app.patient import schemas as patient_schemas
from app.patient.schemas import DeletePatientSchema
from app.patient.services import PatientService
from app.settings import config

api = APIRouter(prefix=config.BASE_PATH)


@api.post(
    "/CreatePatient",
    responses={
        status.HTTP_200_OK: {"model": patient_schemas.PatientSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
    },
    operation_id="create-patient",
)
@remove_cache("Patient")
async def create_patient_api(
    payload: patient_schemas.CreatePatientSchema,
    patient_service: PatientService = Depends(),
) -> patient_schemas.PatientSchema:
    patient = await patient_service.create_patient(payload)
    return patient_schemas.PatientSchema.model_validate(patient)


@api.post(
    "/UpdatePatientInfo",
    responses={
        status.HTTP_200_OK: {"model": patient_schemas.PatientSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
    },
    operation_id="update-patient",
)
@remove_cache("Bed")
@remove_cache("Patient")
@remove_cache("Observation")
async def update_patient_info_command(
    payload: patient_schemas.UpdatePatientSchema,
    patient_service: PatientService = Depends(),
) -> patient_schemas.PatientSchema:
    patient = await patient_service.update_patient(payload)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return patient_schemas.PatientSchema.model_validate(patient)


@api.post(
    "/DeletePatient",
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
    },
    operation_id="delete-patient",
)
@remove_cache("Bed")
@remove_cache("Patient")
@remove_cache("Observation")
async def delete_patient_command(
    response: Response,
    payload: DeletePatientSchema,
    patient_service: PatientService = Depends(),
) -> Response:
    await patient_service.delete_patient(payload.id)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
