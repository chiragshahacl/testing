from cache import remove_cache
from fastapi import APIRouter, Depends, Response
from starlette import status

from app.encounter import schemas as encounter_schemas
from app.encounter.schemas import DismissPatientAdmissionPayload
from app.encounter.services import EncounterService

api = APIRouter()


@api.post(
    "/PlanPatientAdmission",
    responses={
        status.HTTP_200_OK: {"model": encounter_schemas.EncounterSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
    },
    operation_id="start-encounter",
)
@remove_cache("Bed")
async def plan_patient_admission_api(
    payload: encounter_schemas.PatientAdmissionSchema,
    encounter_service: EncounterService = Depends(),
) -> encounter_schemas.EncounterSchema:
    encounter = await encounter_service.plan_patient_admission(payload.subject_id, payload.bed_id)
    return encounter_schemas.EncounterSchema.model_validate(encounter)


@api.post("/DismissPatientAdmission")
@remove_cache("Bed")
async def dismiss_patient_admission_api(
    payload: DismissPatientAdmissionPayload, encounter_service: EncounterService = Depends()
) -> Response:
    await encounter_service.dismiss_encounter_by_patient_id(payload.patient_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
