from fastapi import APIRouter
from starlette import status

from src.emulator.memory_registry import DataManager
from src.monitor.schemas import PatientMonitorResourcesSchema

api = APIRouter()


@api.get(
    "/monitor",
    responses={
        status.HTTP_200_OK: {"model": PatientMonitorResourcesSchema},
    },
    operation_id="get-emulated-patient-monitors",
)
def get_emulated_patient_monitors() -> PatientMonitorResourcesSchema:
    data_manager = DataManager()
    patient_monitors = list(data_manager.patient_monitors_registry.values())
    return PatientMonitorResourcesSchema.from_data_model(patient_monitors)
