import uuid

from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.common.models import Entity


class SystemSettings(Entity):
    __tablename__ = "system_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    patient_vitals_retention_period_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    def as_dict(self) -> dict:
        return {
            "id": str(self.id),
            "patient_vitals_retention_period_ms": self.patient_vitals_retention_period_ms,
        }
