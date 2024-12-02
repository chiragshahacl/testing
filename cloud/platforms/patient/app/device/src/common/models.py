# pylint: disable=E1102, R0801
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from app.common.models import Bed, Entity

if TYPE_CHECKING:
    from app.encounter.models import Encounter


class Device(Entity):
    __tablename__ = "devices"

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True)
    primary_identifier: Mapped[str] = Column(String(255), nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    location_id: Mapped[UUID] = Column(
        UUID(as_uuid=True), ForeignKey("beds.id"), nullable=True, unique=True
    )
    location: Mapped["Bed"] = relationship(
        "Bed",
        back_populates="device",
    )
    model_number: Mapped[str] = Column(String(255), nullable=False, default="sibel", index=True)
    gateway_id: Mapped[UUID] = Column(
        UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True, index=True
    )
    gateway: Mapped["Device"] = relationship(
        "Device",
        backref="children",
        remote_side=[id],
    )
    vital_ranges: Mapped[List["DeviceVitalRange"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    alerts: Mapped[List["DeviceAlert"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    encounter: Mapped["Encounter"] = relationship(
        "Encounter",
        uselist=False,
        back_populates="device",
        cascade="all, delete-orphan",
    )

    subject_identifier: Mapped[str] = Column(String(255), nullable=True)
    audio_pause_enabled: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    audio_enabled: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    updated_at = Column(
        DateTime(timezone=False),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_device_primary_identifier", func.lower(primary_identifier), unique=True),
        Index("ix_device_location_id", location_id, unique=True),
    )

    def as_dict(self):
        return {
            "id": str(self.id),
            "primary_identifier": self.primary_identifier,
            "model_number": self.model_number,
            "name": self.name,
            "location_id": self.location_id,
            "gateway_id": self.gateway_id,
            "audio_pause_enabled": self.audio_pause_enabled,
            "audio_enabled": self.audio_enabled,
        }


class DeviceVitalRange(Entity):
    __tablename__ = "device_vital_ranges"

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = Column(String, nullable=False)
    upper_limit: Mapped[float] = Column(Float, nullable=True)
    lower_limit: Mapped[float] = Column(Float, nullable=True)
    alert_condition_enabled: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    device_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    device: Mapped["Device"] = relationship(back_populates="vital_ranges")
    updated_at = Column(
        DateTime(timezone=False),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "upper_limit": self.upper_limit,
            "lower_limit": self.lower_limit,
            "device_id": self.device_id,
        }


class DeviceAlert(Entity):
    __tablename__ = "device_alerts"

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = Column(String, nullable=False)
    device_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = Column(String, nullable=True)

    device: Mapped["Device"] = relationship(back_populates="alerts")
    updated_at = Column(
        DateTime(timezone=False),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_unique_device_id_with_code", func.lower(code), device_id, unique=True),
    )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "device_id": self.device_id,
            "priority": self.priority,
        }
