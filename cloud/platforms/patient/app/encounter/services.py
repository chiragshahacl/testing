# pylint: disable=too-many-arguments
from typing import Optional
from uuid import UUID

from fastapi import Depends
from loguru import logger
from starlette.requests import Request

from app.bed.services import PatientNotFound
from app.common.exceptions import BaseValidationException
from app.common.models import Patient
from app.common.schemas import ErrorSchema
from app.device.src.common.models import Device
from app.device.src.device.repository import ReadDeviceRepository
from app.device.src.device.services import DeviceNotFound
from app.encounter.enums import EncounterStatus
from app.encounter.events import (
    CancelPatientEncounter,
    CompletePatientEncounter,
    DismissPatientEncounter,
    PlanPatientEncounter,
    StartPatientEncounter,
)
from app.encounter.models import Encounter
from app.encounter.repository import ReadEncounterRepository
from app.encounter.streams import EncounterEventStream
from app.patient.repository import ReadPatientRepository


class EncounterNotFound(BaseValidationException):
    def __init__(self):
        self.error = ErrorSchema(
            loc=["body"],
            msg="Encounter not found for patient",
            type="value_error.encounter_not_found",
        )


class EncounterDismissError(BaseValidationException):
    def __init__(self):
        self.error = ErrorSchema(
            loc=[""],
            msg="Cannot dismiss non cancelled encounter",
            type="value_error.cannot_dismiss_encounter",
        )


class ExistingEncounterInProgress(BaseValidationException):
    def __init__(self):
        self.error = ErrorSchema(
            loc=[""],
            msg="Cannot plan encounter: "
            "in-progress encounter found for the selected patient and/or device",
            type="value_error.cannot_plan_encounter",
        )


class EncounterService:
    def __init__(
        self,
        request: Request,
        event_stream: EncounterEventStream = Depends(),
        read_encounter_repository: ReadEncounterRepository = Depends(),
        read_patient_repository: ReadPatientRepository = Depends(),
        read_device_repository: ReadDeviceRepository = Depends(),
    ):
        self.username = request.state.username
        self.event_stream = event_stream
        self.read_encounter_repository = read_encounter_repository
        self.read_patient_repository = read_patient_repository
        self.read_device_repository = read_device_repository

    async def _cancel_encounter(self, encounter: Encounter, delete: bool = False) -> None:
        event = CancelPatientEncounter(self.username)
        if delete:
            await self.event_stream.delete(event, encounter)
        else:
            await self.event_stream.add(event, encounter)

    async def _remove_encounter(self, encounter: Encounter) -> None:
        if encounter.status == EncounterStatus.IN_PROGRESS:
            await self._complete_encounter(encounter)
        else:
            await self._cancel_encounter(encounter, delete=True)

    async def _complete_encounter(self, encounter: Encounter) -> None:
        event = CompletePatientEncounter(self.username)
        await self.event_stream.delete(event, encounter, related_entity_id=encounter.subject_id)

    async def _get_and_clean_encounters(
        self, patient_id: UUID, device_id: UUID, clean_in_progress_encounters: bool = True
    ) -> Optional[Encounter]:
        current_encounter = None
        encounters = await self.read_encounter_repository.get_encounters(
            patient_id, device_id, lock=True
        )
        for encounter in encounters:
            if encounter.subject_id == patient_id and encounter.device_id == device_id:
                current_encounter = encounter
            else:
                if encounter.status != EncounterStatus.IN_PROGRESS or clean_in_progress_encounters:
                    logger.info(f"Removing existing encounter: {encounter}")
                    await self._remove_encounter(encounter)
                else:
                    raise ExistingEncounterInProgress()
        return current_encounter

    async def _start_encounter_by_patient(self, patient: Patient, device: Device) -> Encounter:
        current_encounter = await self._get_and_clean_encounters(patient.id, device.id)
        event = StartPatientEncounter(self.username, patient, device)
        encounter = await self.event_stream.add(
            event, current_encounter, related_entity_id=patient.id
        )
        return encounter

    async def plan_patient_admission(self, patient_id: UUID, location_id: UUID) -> Encounter:
        patient = await self.read_patient_repository.get_patient_by_id(patient_id)
        if not patient:
            raise PatientNotFound
        device = await self.read_device_repository.get_device_by_location(location_id)
        if not device:
            raise DeviceNotFound

        current_encounter = await self._get_and_clean_encounters(
            patient.id, device.id, clean_in_progress_encounters=False
        )
        if current_encounter and current_encounter.status == EncounterStatus.IN_PROGRESS:
            raise ExistingEncounterInProgress()
        if current_encounter:
            await self._remove_encounter(current_encounter)

        event = PlanPatientEncounter(self.username, patient, device)
        encounter = await self.event_stream.add(event, None, related_entity_id=patient.id)
        return encounter

    async def start_encounter_by_ids(self, patient_id: UUID, device_id: UUID) -> Encounter:
        patient = await self.read_patient_repository.get_patient_by_id(patient_id)
        if not patient:
            raise PatientNotFound
        device = await self.read_device_repository.get_device_by_id(device_id)
        if not device:
            raise DeviceNotFound
        encounter = await self._start_encounter_by_patient(patient, device)
        return encounter

    async def start_encounter_by_identifiers(
        self, patient_identifier: str, device_identifier: str
    ) -> Encounter:
        patient = await self.read_patient_repository.get_patient_by_identifier(patient_identifier)
        if not patient:
            raise PatientNotFound
        device = await self.read_device_repository.get_device_by_identifier(device_identifier)
        if not device:
            raise DeviceNotFound
        encounter = await self._start_encounter_by_patient(patient, device)
        return encounter

    async def _complete_encounter_by_patient(self, patient: Patient) -> None:
        encounter = await self.read_encounter_repository.get_patient_encounter(patient.id)

        if encounter.status != EncounterStatus.IN_PROGRESS:
            logger.warning(f"Completing encounter with status: {encounter.status}")

        await self._complete_encounter(encounter)

    async def complete_encounter_by_patient_id(self, patient_id: UUID) -> None:
        patient = await self.read_patient_repository.get_patient_by_id(patient_id)
        if not patient:
            raise PatientNotFound
        await self._complete_encounter_by_patient(patient)

    async def dismiss_encounter_by_patient_id(self, patient_id: UUID) -> None:
        patient = await self.read_patient_repository.get_patient_by_id(patient_id)
        if not patient:
            raise PatientNotFound
        encounter = await self.read_encounter_repository.get_patient_encounter(patient.id)
        if not encounter:
            raise EncounterNotFound
        if encounter.status != EncounterStatus.CANCELLED:
            raise EncounterDismissError
        event = DismissPatientEncounter(self.username)
        await self.event_stream.delete(event, encounter)

    async def cancel_encounter_by_identifiers(
        self, patient_identifier: str, device_identifier: str
    ) -> None:
        encounter = await self.read_encounter_repository.get_encounter_by_identifiers(
            patient_identifier, device_identifier
        )
        if not encounter:
            raise EncounterNotFound

        await self._cancel_encounter(encounter, delete=False)
