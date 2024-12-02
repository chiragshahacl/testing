import uuid
from typing import Iterable, Optional, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, func, or_, select, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query, aliased, selectinload

from app.common.database import get_db_session
from app.device.src.common.models import Device, DeviceAlert, DeviceVitalRange
from app.device.src.device import schemas as device_schemas
from app.encounter.models import Encounter

DEVICE_DEFAULT_VITALS = [
    {"code": "258422", "upper_limit": 110, "lower_limit": 50},  # DiaBP
    {"code": "258421", "upper_limit": 160, "lower_limit": 90},  # SysBP
    {"code": "258418", "upper_limit": 120, "lower_limit": 45},  # HR
    {"code": "258424", "upper_limit": 102.2, "lower_limit": 93.2},  # skin temp
    {"code": "258425", "upper_limit": 102.2, "lower_limit": 93.2},  # body temp
    {"code": "258420", "upper_limit": 100, "lower_limit": 85},  # SpO2
    {"code": "258427", "upper_limit": 120, "lower_limit": 45},  # PR
    {"code": "8574701", "upper_limit": 0, "lower_limit": None},  # Fall
    {"code": "258426", "upper_limit": 120, "lower_limit": None},  # Body Position
    {"code": "258419", "upper_limit": 30, "lower_limit": 5},  # RR
]


class ListFilterQueryBuilder:
    def __init__(self, query, param: device_schemas.DeviceQueryParams) -> None:
        self.query = query
        self.params = param

    def _apply_device_code_filter(self) -> None:
        if self.params.device_code:
            self.query = self.query.filter(Device.model_number == self.params.device_code)

    def _apply_location_filer(self) -> None:
        if self.params.location_id:
            device_alias = aliased(Device)
            self.query = self.query.join(device_alias, Device.gateway).filter(
                or_(
                    Device.location_id.in_(self.params.location_id),
                    device_alias.location_id.in_(self.params.location_id),
                )
            )

    def _apply_gateway_filter(self) -> None:
        if self.params.gateway:
            self.query = self.query.filter(Device.gateway_id == self.params.gateway)

    def _apply_is_gateway_filter(self) -> None:
        if self.params.is_gateway is not None:
            if self.params.is_gateway:
                self.query = self.query.filter(
                    Device.gateway_id == None  # pylint: disable=C0121 # noqa: E711
                )
            else:
                self.query = self.query.filter(
                    Device.gateway_id != None  # pylint: disable=C0121 # noqa: E711
                )

    def get(self) -> Query:
        self._apply_device_code_filter()
        self._apply_location_filer()
        self._apply_gateway_filter()
        self._apply_is_gateway_filter()
        return self.query


class ReadDeviceRepository:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self.db_session = db_session
        self.base_query = select(Device)

    async def get_device_by_identifier(self, identifier: Optional[str]) -> Optional[Device]:
        if not identifier:
            return None
        result = await self.db_session.execute(
            self.base_query.where(func.lower(Device.primary_identifier) == identifier.lower())
            .options(selectinload(Device.vital_ranges))
            .options(selectinload(Device.alerts))
        )
        return result.scalars().first()

    async def get_device_by_id(
        self, identifier: UUID, include_subject: bool = False
    ) -> Optional[Device]:
        query = self.base_query.where(Device.id == identifier)
        if include_subject:
            query = query.options(selectinload(Device.encounter).subqueryload(Encounter.subject))
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_device_by_location(self, identifier: UUID) -> Optional[Device]:
        result = await self.db_session.execute(
            self.base_query.where(Device.location_id == identifier)
        )
        return result.scalars().first()

    async def get_all_devices(self, params: device_schemas.DeviceQueryParams) -> Sequence[Device]:
        query = ListFilterQueryBuilder(self.base_query, params).get()
        # minimize the number of queries
        query = query.options(selectinload(Device.vital_ranges))
        query = query.options(selectinload(Device.alerts))
        devices = await self.db_session.execute(query)
        return devices.scalars().unique().all()

    async def get_all_devices_by_primary_identifiers(
        self, primary_identifiers: Iterable[str]
    ) -> Sequence[Device]:
        stmt = select(Device).where(Device.primary_identifier.in_(primary_identifiers))
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_gateway_sensors(self, gateway_id: UUID):
        result = await self.db_session.execute(
            select(Device).where(Device.gateway_id == gateway_id)
        )
        return result.scalars().all()

    async def get_device_vital_ranges(
        self,
        device_id: UUID,
    ) -> Sequence[DeviceVitalRange]:
        result = await self.db_session.execute(
            select(DeviceVitalRange).where(DeviceVitalRange.device_id == device_id)
        )
        return result.scalars().all()

    async def get_device_vital_ranges_by_identifier(
        self,
        identifier: str,
    ) -> Sequence[DeviceVitalRange]:
        stmt = (
            select(DeviceVitalRange)
            .join(Device, Device.id == DeviceVitalRange.device_id)
            .where(func.lower(Device.primary_identifier) == identifier.lower())
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().all()


class VitalsRangeRepository:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self.db_session = db_session

    async def add_default_vital_ranges(self, device_id: UUID) -> None:
        default_vital_schemas = []
        for v_range in DEVICE_DEFAULT_VITALS:
            create_payload = DeviceVitalRange(
                id=uuid.uuid4(),
                code=v_range["code"],
                upper_limit=v_range["upper_limit"],
                lower_limit=v_range["lower_limit"],
                device_id=device_id,
            )
            default_vital_schemas.append(create_payload)
        self.db_session.add_all(default_vital_schemas)
        await self.db_session.flush()


class DeviceAlertRepository:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self.db_session = db_session

    async def delete_alerts_by_device(self, device_ids: list[str]) -> None:
        stmt = delete(DeviceAlert).where(DeviceAlert.device_id.in_(device_ids))
        await self.db_session.execute(stmt)

    async def bulk_add(self, alerts: Iterable[DeviceAlert]):
        stmt = (
            insert(DeviceAlert)
            .values(
                [
                    {
                        "id": alert.id,
                        "code": alert.code,
                        "device_id": alert.device_id,
                        "priority": alert.priority,
                    }
                    for alert in alerts
                ]
            )
            .on_conflict_do_nothing()
        )
        await self.db_session.execute(stmt)

    async def bulk_delete(self, alerts: Iterable[DeviceAlert]) -> None:
        stmt = delete(DeviceAlert).where(
            tuple_(
                DeviceAlert.code,
                DeviceAlert.device_id,
            ).in_(
                (
                    alert.code,
                    alert.device_id,
                )
                for alert in alerts
            )
        )
        await self.db_session.execute(stmt)
