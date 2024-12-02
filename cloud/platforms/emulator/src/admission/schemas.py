from pydantic import BaseModel


class RejectPatientAdmissionSchema(BaseModel):
    patient_monitor_primary_identifier: str
    patient_primary_identifier: str
