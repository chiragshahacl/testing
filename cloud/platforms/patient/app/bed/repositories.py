from typing import List, Optional, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.database import get_db_session
from app.common.models import Bed, BedGroup, Patient
from app.device.src.common.models import Device
from app.encounter.models import Encounter


class ReadBedRepository:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self._db_session = db_session

    async def get_bed(self, bed_id: UUID, lock: bool = False) -> Optional[Bed]:
        stmt = select(Bed).where(Bed.id == bed_id)
        if lock:
            stmt = stmt.with_for_update(of=Bed)
        result = await self._db_session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_beds(self, with_ids: List[UUID] = None, lock: bool = False) -> Sequence[Bed]:
        stmt = select(Bed)
        if with_ids is not None:
            stmt = stmt.where(Bed.id.in_(with_ids))
        if lock:
            stmt = stmt.with_for_update()
        result = await self._db_session.execute(stmt)
        return result.scalars().all()

    async def get_beds_with_patients(
        self, with_ids: List[UUID] = None
    ) -> list[tuple[Bed, Optional[Patient], Optional[Encounter]]]:
        stmt = (
            select(Bed, Patient, Encounter)
            .join(Device, Device.location_id == Bed.id, isouter=True)
            .join(Encounter, Encounter.device_id == Device.id, isouter=True)
            .join(Patient, Patient.id == Encounter.subject_id, isouter=True)
        )
        if with_ids is not None:
            stmt = stmt.where(Bed.id.in_(with_ids))
        result = await self._db_session.execute(stmt)
        return result.all()

    async def get_bed_groups(
        self, with_ids: List[UUID] = None, lock: bool = False
    ) -> Sequence[BedGroup]:
        stmt = select(BedGroup).options(selectinload(BedGroup.beds))
        if with_ids is not None:
            stmt = stmt.where(BedGroup.id.in_(with_ids))
        if lock:
            stmt = stmt.with_for_update()
        result = await self._db_session.execute(stmt)
        return result.scalars().all()

    async def get_bed_group_by_id(self, group_id: UUID, lock: bool = False) -> Optional[BedGroup]:
        stmt = select(BedGroup).where(BedGroup.id == group_id).options(selectinload(BedGroup.beds))
        if lock:
            stmt = stmt.with_for_update()
        result = await self._db_session.execute(stmt)
        return result.scalars().first()

    async def get_beds_for_group(
        self, group_id: UUID
    ) -> list[tuple[Bed, Optional[Patient], Optional[Encounter]]]:
        stmt = (
            select(Bed, Patient, Encounter)
            .join(BedGroup.beds)
            .where(BedGroup.id == group_id)
            .join(Device, Device.location_id == Bed.id, isouter=True)
            .join(Encounter, Encounter.device_id == Device.id, isouter=True)
            .join(Patient, Patient.id == Encounter.subject_id, isouter=True)
        )
        result = await self._db_session.execute(stmt)
        return result.all()
