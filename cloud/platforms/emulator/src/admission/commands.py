from fastapi import APIRouter
from starlette import status
from starlette.responses import Response

from src.admission.schemas import RejectPatientAdmissionSchema
from src.broker import publish_reject_patient_admission

api = APIRouter()


@api.post(
    "/RejectAdmission",
    operation_id="reject-patient-admission",
)
async def reject_patient_admission(
    payload: RejectPatientAdmissionSchema,
) -> Response:
    await publish_reject_patient_admission(
        payload.patient_monitor_primary_identifier, payload.patient_primary_identifier
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
