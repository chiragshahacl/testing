import uuid
from datetime import datetime
from typing import Optional

from app.common.event_sourcing.events import Event
from app.common.models import Patient
from app.device.src.common.models import Device
from app.encounter.enums import EncounterStatus
from app.encounter.models import Encounter


class PlanPatientEncounter(Event):
    display_name: str = "Patient admission planned"
    event_type: str = "PATIENT_ENCOUNTER_PLANNED"
    is_backfill: str = "0"

    def __init__(self, username: str, patient: Patient, device: Device):
        super().__init__(username)
        self.patient = patient
        self.device = device
        self.status = EncounterStatus.PLANNED

    def process(self, entity: Optional[Encounter] = None) -> Encounter:
        return Encounter(
            id=uuid.uuid4(),
            device=self.device,
            subject=self.patient,
            status=self.status,
            created_at=datetime.now(),
        )


class StartPatientEncounter(Event):
    display_name: str = "Patient admitted"
    event_type: str = "PATIENT_ENCOUNTER_STARTED"
    is_backfill: str = "0"

    def __init__(self, username: str, patient: Patient, device: Device):
        super().__init__(username)
        self.patient = patient
        self.device = device
        self.status = EncounterStatus.IN_PROGRESS

    def process(self, entity: Optional[Encounter] = None) -> Encounter:
        if entity:
            entity.status = self.status
            entity.end_time = None
            return entity
        return Encounter(
            id=uuid.uuid4(),
            device=self.device,
            subject=self.patient,
            status=self.status,
            start_time=datetime.now(),
            created_at=datetime.now(),
        )


class CancelPatientEncounter(Event):
    display_name: str = "Encounter cancelled"
    event_type: str = "PATIENT_ENCOUNTER_CANCELLED"
    is_backfill: str = "0"

    def __init__(self, username: str):
        super().__init__(username)
        self.status = EncounterStatus.CANCELLED

    def process(self, entity: Encounter) -> Encounter:
        entity.status = self.status
        entity.end_time = datetime.now()
        return entity


class CompletePatientEncounter(Event):
    display_name: str = "Encounter completed"
    event_type: str = "PATIENT_ENCOUNTER_COMPLETED"
    is_backfill: str = "0"

    def __init__(
        self,
        username: str,
    ):
        super().__init__(username)
        self.status = EncounterStatus.COMPLETED

    def process(self, entity: Encounter) -> Encounter:
        entity.status = self.status
        now = datetime.now()
        if not entity.start_time:
            entity.start_time = now
        entity.end_time = now
        return entity


class DismissPatientEncounter(Event):
    display_name: str = "Patient admission dismissed"
    event_type: str = "PATIENT_ADMISSION_DISMISSED"
    is_backfill: str = "0"

    def process(self, entity: Encounter) -> Encounter:
        return entity
