from datetime import datetime
from typing import Iterable, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db_session
from app.common.models import AlertLog, Observation


class AlertsLogRepository:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self.db_session = db_session

    async def get(
        self,
        patient_id: UUID,
        device_primary_identifier: str,
        code: str,
        determination_time: datetime,
    ) -> Optional[AlertLog]:
        stmt = (
            select(AlertLog)
            .where(AlertLog.patient_id == patient_id)
            .where(AlertLog.device_primary_identifier == device_primary_identifier)
            .where(AlertLog.code == code)
            .where(AlertLog.determination_time == determination_time)
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().one_or_none()

    async def delete_alerts_for_patient(self, patient_id: UUID) -> None:
        stmt = delete(AlertLog).where(AlertLog.patient_id == patient_id)
        await self.db_session.execute(stmt)


class ObservationRepository:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self.db_session = db_session

    async def bulk_add_alerts(self, alerts: Iterable[Observation]):
        stmt = (
            insert(Observation)
            .values(
                [
                    {
                        "id": alert.id,
                        "category": alert.category,
                        "code": alert.code,
                        "subject_id": alert.subject_id,
                        "effective_dt": alert.effective_dt,
                        "value_text": alert.value_text,
                        "device_code": alert.device_code,
                        "device_primary_identifier": alert.device_primary_identifier,
                        "is_alert": alert.is_alert,
                    }
                    for alert in alerts
                ]
            )
            .on_conflict_do_nothing()
        )
        await self.db_session.execute(stmt)

    async def bulk_delete_alerts(self, alerts: Iterable[Observation]) -> None:
        stmt = delete(Observation).where(
            tuple_(
                Observation.code,
                Observation.device_primary_identifier,
            ).in_(
                (
                    alert.code,
                    alert.device_primary_identifier,
                )
                for alert in alerts
            )
        )
        await self.db_session.execute(stmt)
