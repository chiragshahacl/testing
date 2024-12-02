from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.common.database import get_db_session
from app.common.models import Patient
from app.device.src.common.models import Device
from app.encounter.models import Encounter


class ReadEncounterRepository:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self.db_session = db_session

    async def get_encounter_by_identifiers(
        self, patient_primary_identifier: str, device_primary_identifier: str
    ) -> Optional[Encounter]:
        stmt = select(Encounter).where(
            Encounter.subject.has(
                func.lower(Patient.primary_identifier) == patient_primary_identifier.lower()
            ),
            Encounter.device.has(
                func.lower(Device.primary_identifier) == device_primary_identifier.lower()
            ),
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_encounters(
        self, patient_id: UUID, device_id: UUID, lock: bool = False
    ) -> list[Encounter]:
        stmt = select(Encounter).where(
            or_(
                Encounter.device_id == device_id,
                Encounter.subject_id == patient_id,
            )
        )
        if lock:
            lock_stmt = (
                stmt.options(lazyload(Encounter.subject))
                .options(lazyload(Encounter.device))
                .with_for_update()
            )
            await self.db_session.execute(lock_stmt)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_patient_encounter(self, patient_id: UUID) -> Optional[Encounter]:
        stmt = select(Encounter).where(Encounter.subject_id == patient_id)
        result = await self.db_session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_device_encounter(
        self,
        device_primary_identifier: str,
    ) -> Optional[Encounter]:
        stmt = select(Encounter).where(
            Encounter.device.has(Device.primary_identifier == device_primary_identifier)
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().one_or_none()
