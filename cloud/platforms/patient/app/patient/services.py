from typing import Optional
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.exc import IntegrityError

from app.common import schemas as common_schemas
from app.common.exceptions import BaseValidationException
from app.common.models import AlertLog
from app.patient import schemas as patient_schemas
from app.patient.events import (
    CreatePatientEvent,
    DeletePatientEvent,
    UpdatePatientInfoEvent,
)
from app.patient.repository import ReadPatientRepository
from app.patient.schemas import SessionPhysiologicalAlert
from app.patient.stream import PatientEventStream


class PatientAlreadyExists(BaseValidationException):
    def __init__(self) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body", "id"],
            msg="Patient already exists",
            type="value_error.already_in_use",
        )


class PatientPrimaryIdentifierInUse(BaseValidationException):
    def __init__(self) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body", "primary_identifier"],
            msg="Primary identifier already in use",
            type="value_error.already_in_use",
        )


class PatientService:
    def __init__(
        self,
        request: Request,
        event_stream: PatientEventStream = Depends(),
        read_patient_repository: ReadPatientRepository = Depends(),
    ):
        self.username = request.state.username
        self.event_stream = event_stream
        self.read_patient_repository = read_patient_repository

    async def get_patient(self, patient_id: UUID) -> Optional[patient_schemas.PatientSchema]:
        patient = await self.read_patient_repository.get_patient_by_id(patient_id)
        if not patient:
            return None
        return patient_schemas.PatientSchema.model_validate(patient)

    async def get_patient_by_identifier(
        self, identifier_id: str
    ) -> Optional[patient_schemas.PatientSchema]:
        patient = await self.read_patient_repository.get_patient_by_identifier(identifier_id)
        if not patient:
            return None
        return patient_schemas.PatientSchema.model_validate(patient)

    async def get_patients(
        self, params: patient_schemas.PatientQueryParams
    ) -> patient_schemas.PatientResources:
        patients = await self.read_patient_repository.get_patients(params)
        return patient_schemas.PatientResources.model_construct(
            resources=[patient_schemas.PatientSchema.model_validate(p) for p in patients]
        )

    async def get_patients_count(
        self, params: patient_schemas.PatientQueryParams
    ) -> patient_schemas.PatientCount:
        count = await self.read_patient_repository.count_patients(params)
        return patient_schemas.PatientCount.model_construct(total=count)

    async def create_patient(
        self, patient_schema: patient_schemas.CreatePatientSchema
    ) -> patient_schemas.PatientSchema:
        try:
            event = CreatePatientEvent(self.username, patient_schema)
            patient = await self.event_stream.add(event, None)
        except IntegrityError as exc:
            if "patients_primary_identifier_key" in exc.args[0]:
                raise PatientPrimaryIdentifierInUse from exc
            if "patients_pkey" in exc.args[0]:
                raise PatientAlreadyExists from exc
            raise exc
        return patient

    async def update_patient(
        self, patient_schema: patient_schemas.UpdatePatientSchema
    ) -> Optional[patient_schemas.PatientSchema]:
        patient = await self.read_patient_repository.get_patient_by_id(patient_schema.id)
        if not patient:
            return None
        event = UpdatePatientInfoEvent(self.username, patient_schema)
        updated_patient = await self.event_stream.add(event, patient)
        return patient_schemas.PatientSchema.model_validate(updated_patient)

    async def delete_patient(
        self,
        patient_id: UUID,
    ) -> None:
        patient = await self.read_patient_repository.get_patient_by_id(patient_id)
        if patient:
            event = DeletePatientEvent(self.username)
            await self.event_stream.delete(event, patient)

    async def get_patient_observations(
        self,
        params: patient_schemas.PatientObservationsQueryParams,
    ) -> patient_schemas.PatientObservationResources:
        patient_observations = await self.read_patient_repository.get_patient_observations(params)
        return patient_schemas.PatientObservationResources.model_construct(
            resources=[
                patient_schemas.PatientObservation.model_validate(observation)
                for observation in patient_observations
            ]
        )

    async def get_physiological_alerts(self, patient_id: str) -> list[SessionPhysiologicalAlert]:
        alerts = await self.read_patient_repository.get_physiological_alerts(patient_id)

        paired_alerts: list[SessionPhysiologicalAlert] = []
        active_alerts: dict[tuple[str, str], AlertLog] = {}

        for alert in alerts:
            key = (alert.code, alert.device_primary_identifier)

            if alert.active:
                active_alerts[key] = alert
            else:
                if key in active_alerts:
                    activation_alert = active_alerts.pop(key)
                    paired_alerts.append(
                        SessionPhysiologicalAlert(
                            code=activation_alert.code,
                            start_determination_time=activation_alert.determination_time,
                            end_determination_time=alert.determination_time,
                            value_text=activation_alert.value_text,
                            device_primary_identifier=activation_alert.device_primary_identifier,
                            device_code=activation_alert.device_code,
                            trigger_lower_limit=activation_alert.trigger_lower_limit,
                            trigger_upper_limit=activation_alert.trigger_upper_limit,
                        )
                    )

        return paired_alerts
