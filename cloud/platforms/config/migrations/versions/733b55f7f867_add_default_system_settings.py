"""
Add default system settings
"""

import uuid

from alembic import op
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column

from app.settings import config

revision = "733b55f7f867"
down_revision = "3dc90d727394"
branch_labels = None
depends_on = None

Base = declarative_base()


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    patient_vitals_retention_period_ms: Mapped[int] = mapped_column(Integer, nullable=False)


def upgrade() -> None:
    session = Session(bind=op.get_bind())
    settings = SystemSettings(
        id=uuid.uuid4(),
        patient_vitals_retention_period_ms=config.PATIENT_VITALS_DEFAULT_KAFKA_TOPIC_RETENTION_MS,
    )
    session.add(settings)
    session.commit()


def downgrade() -> None:
    session = Session(bind=op.get_bind())
    session.query(SystemSettings).delete()
