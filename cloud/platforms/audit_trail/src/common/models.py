from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# pylint: disable=E1102
class InternalAudit(Base):
    __tablename__ = "internal_audit"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(Integer, primary_key=True)
    entity_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=False), nullable=False, index=True)
    data = Column(JSONB, nullable=True)
    event_name = Column(String(100), nullable=False)
    event_type = Column(String(100), nullable=True)
    message_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    emitted_by = Column(String(255), nullable=False)
    performed_by = Column(String(255), nullable=False)
    event_data = Column(JSONB, nullable=True)

    def as_dict(self):
        return {
            "record_id": self.id,
            "entity_id": self.entity_id,
            "timestamp": self.timestamp,
            "data": self.data,
            "emitted_by": self.emitted_by,
            "performed_by": self.performed_by,
        }
