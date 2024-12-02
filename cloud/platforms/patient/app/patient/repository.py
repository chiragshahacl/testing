from typing import Optional, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import asc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query

from app.common.database import get_db_session
from app.common.models import AlertLog, Observation, Patient
from app.device.src.common.models import Device
from app.encounter.models import Encounter
from app.patient import schemas as patient_schemas


# pylint: disable=E1102
class ListFilterQueryBuilder:
    query: Query
    params: patient_schemas.PatientQueryParams

    def __init__(self, query: Query, param: patient_schemas.PatientQueryParams) -> None:
        self.query = query
        self.params = param

    def _apply_identifier_filter(self) -> None:
        if self.params.identifier:
            self.query = self.query.filter(
                func.lower(Patient.primary_identifier) == self.params.identifier.lower()
            )

    def get(self) -> Query:
        self._apply_identifier_filter()
        return self.query


class ListObservationsQueryBuilder:
    query: Query
    params: patient_schemas.PatientObservationsQueryParams

    def __init__(
        self, query: Query, params: patient_schemas.PatientObservationsQueryParams
    ) -> None:
        self.query = query
        self.params = params

    def _apply_subject_filter(self) -> None:
        if self.params.patient_ids:
            self.query = self.query.filter(Observation.subject_id.in_(self.params.patient_ids))

    def _apply_alert_filter(self) -> None:
        if self.params.is_alert is not None:
            self.query = self.query.filter(Observation.is_alert == self.params.is_alert)

    def get(self) -> Query:
        self._apply_alert_filter()
        self._apply_subject_filter()
        return self.query


class PaginatedListFilterQueryBuilder(ListFilterQueryBuilder):
    def _apply_pagination(self) -> None:
        offset = (self.params.page_number - 1) * self.params.page_size
        self.query = self.query.offset(offset).limit(self.params.page_size)

    def _apply_order(self) -> None:
        self.query = self.query.order_by(Patient.primary_identifier)

    def get(self) -> Query:
        self.query = super().get()
        self._apply_order()
        return self.query


class ReadPatientRepository:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self.db_session = db_session
        self.base_query = select(Patient)

    async def count_patients(self, params: patient_schemas.PatientQueryParams) -> int:
        query = select(func.count(Patient.id))
        query = ListFilterQueryBuilder(query, params).get()
        patient_count = await self.db_session.execute(query)
        return patient_count.scalar()

    async def get_patients(self, params: patient_schemas.PatientQueryParams) -> Sequence[Patient]:
        query = PaginatedListFilterQueryBuilder(self.base_query, params).get()
        patients = await self.db_session.execute(query)
        return patients.scalars().all()

    async def get_patient_by_id(self, patient_id: UUID) -> Optional[Patient]:
        stmt = select(Patient).where(Patient.id == patient_id)
        result = await self.db_session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_patient_by_identifier(self, identifier_id: Optional[str]) -> Optional[Patient]:
        if identifier_id is None:
            return None
        stmt = select(Patient).where(
            func.lower(Patient.primary_identifier) == identifier_id.lower()
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_patient_by_device_identifier(
        self, device_primary_identifier: str
    ) -> Optional[Patient]:
        stmt = (
            select(Patient, Device)
            .join(Encounter, Encounter.subject_id == Patient.id)
            .join(Device, Device.id == Encounter.device_id)
            .where(func.lower(Device.primary_identifier) == device_primary_identifier.lower())
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_patient_observations(
        self,
        params: patient_schemas.PatientObservationsQueryParams,
    ) -> Sequence[Observation]:
        query = select(Observation)
        query = ListObservationsQueryBuilder(query, params).get()
        patient_observations = await self.db_session.execute(query)
        return patient_observations.scalars().all()

    async def get_sensor_observations(
        self,
        device_primary_identifier: str,
    ) -> Sequence[Observation]:
        query = select(Observation).filter(
            Observation.device_primary_identifier == device_primary_identifier
        )
        sensor_observations = await self.db_session.execute(query)
        return sensor_observations.scalars().all()

    async def get_alerts(
        self, device_code: str, subject_id: UUID, code: str
    ) -> Sequence[Observation]:
        stmt = select(Observation).where(
            or_(
                Observation.device_code == device_code,
                Observation.device_code.is_(None),
            ),
            Observation.subject_id == subject_id,
            Observation.code == code,
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_physiological_alerts(self, patient_id: str) -> list[AlertLog]:
        stmt = (
            select(AlertLog)
            .where(AlertLog.patient_id == patient_id)
            .order_by(asc(AlertLog.determination_time))
        )
        results = await self.db_session.execute(stmt)

        return results.scalars().all()
