# pylint: disable=E1102, R0801
from datetime import datetime
from typing import Any, Dict

import sqlalchemy
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.common.models import Entity, Patient
from app.device.src.common.models import Device
from app.encounter.enums import EncounterStatus


class Encounter(Entity):
    __tablename__ = "encounters"

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True)
    subject_id: Mapped[UUID] = Column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, unique=True
    )
    device_id: Mapped[UUID] = Column(
        UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, unique=True
    )
    status: Mapped[EncounterStatus] = mapped_column(
        sqlalchemy.Enum(EncounterStatus, name="encounter_status")
    )
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    start_time: Mapped[datetime] = Column(DateTime(timezone=False), nullable=True)
    end_time: Mapped[datetime] = Column(DateTime(timezone=False), nullable=True)

    subject: Mapped[Patient] = relationship("Patient", back_populates="encounter", lazy="joined")
    device: Mapped[Device] = relationship("Device", back_populates="encounter", lazy="joined")

    __table_args__ = (
        Index("ix_encounter_subject_id", subject_id, unique=True),
        Index("ix_encounter_device_id", device_id, unique=True),
    )

    def __repr__(self) -> str:
        return (
            f"<Encounter PM:{self.device.primary_identifier}"
            f", Patient:{self.subject.primary_identifier}>"
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status.value,
            "created_at": self.created_at,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "device": self.device.as_dict(),
            "patient": self.subject.as_dict(),
        }
