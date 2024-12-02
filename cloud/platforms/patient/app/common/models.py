from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List

from sqlalchemy import (
    DECIMAL,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    String,
    Table,
    TypeDecorator,
    cast,
    type_coerce,
)
from sqlalchemy.dialects.postgresql import BYTEA, UUID
from sqlalchemy.orm import Mapped, declarative_base, relationship
from sqlalchemy.sql import func

from app.patient.enums import GenderEnum
from app.settings import config

if TYPE_CHECKING:
    from app.encounter.models import Encounter


Base = declarative_base()


class Entity(Base):
    __abstract__ = True

    def as_dict(self):
        """Dictionary representation of entity"""


# pylint: disable=[W0223, E1102, R0901]
class EnumTypeDecorator(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return value.value if value else None

    def process_result_value(self, value, dialect):
        return self.enum_class(value) if value else None


class GenderType(EnumTypeDecorator):
    enum_class = GenderEnum


bed_group_association_table = Table(
    "bed_group_association_table",
    Base.metadata,
    Column(
        "bed_id",
        UUID(as_uuid=True),
        ForeignKey("beds.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "group_id",
        UUID(as_uuid=True),
        ForeignKey("bed_groups.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class SensitiveString(str):
    """A string that doesn't repr."""

    def __repr__(self):
        return "< redacted >"


class SensitiveStringType(TypeDecorator):
    """Store a string that should not be displayed."""

    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None and not isinstance(value, SensitiveString):
            value = SensitiveString(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = SensitiveString(value)
        return value


class PGPString(TypeDecorator):
    impl = BYTEA
    cache_ok = True

    def __init__(self, passphrase):
        super().__init__()
        self.passphrase = passphrase

    def bind_expression(self, bindparam):
        return func.pgp_sym_encrypt(type_coerce(bindparam, SensitiveStringType), self.passphrase)

    def column_expression(self, column):
        return cast(
            func.pgp_sym_decrypt(column, self.passphrase, type_=SensitiveStringType),
            String,
        )


class PGPDate(TypeDecorator):
    impl = BYTEA
    cache_ok = True

    def __init__(self, passphrase):
        super().__init__()
        self.passphrase = passphrase

    def bind_expression(self, bindparam):
        return func.pgp_sym_encrypt(type_coerce(bindparam, SensitiveStringType), self.passphrase)

    def column_expression(self, column):
        return cast(
            func.pgp_sym_decrypt(column, self.passphrase, type_=Date),
            Date,
        )


if TYPE_CHECKING:
    from app.encounter.models import Encounter


class Patient(Entity):
    __tablename__ = "patients"
    __table_args__ = (
        CheckConstraint("char_length(given_name) > 0", name="given_name_min_len"),
        CheckConstraint("char_length(primary_identifier) > 0", name="primary_identifier_min_len"),
    )
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True)
    primary_identifier: Mapped[str] = Column(String(255), nullable=False, unique=True)
    active: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    given_name: Mapped[str] = Column(
        PGPString(config.DB_ENCRYPTION_KEY.get_secret_value()), nullable=False
    )
    family_name: Mapped[str] = Column(
        PGPString(config.DB_ENCRYPTION_KEY.get_secret_value()), nullable=False
    )
    gender: Mapped[GenderEnum] = Column(GenderType, nullable=False)
    birth_date: Mapped[date] = Column(
        PGPDate(config.DB_ENCRYPTION_KEY.get_secret_value()), nullable=True
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
    encounter: Mapped["Encounter"] = relationship(
        "Encounter",
        uselist=False,
        back_populates="subject",
        cascade="all, delete-orphan",
    )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "primary_identifier": self.primary_identifier,
            "active": self.active,
            "given_name": self.given_name,
            "family_name": self.family_name,
            "gender": self.gender.value,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
        }


class Bed(Entity):
    __tablename__ = "beds"

    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = Column(String(50), nullable=False)
    created_at: Mapped[DateTime] = Column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    groups: Mapped[List["BedGroup"]] = relationship(
        "BedGroup",
        secondary=bed_group_association_table,
        back_populates="beds",
        lazy="selectin",
    )
    device = relationship(
        "Device", back_populates="location", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("char_length(name) > 0", name="name_min_len"),
        Index("ix_unique_bed_name", func.lower(name), unique=True),
    )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
        }


class BedGroup(Entity):
    __tablename__ = "bed_groups"

    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = Column(String(50), nullable=False)
    description: Mapped[str] = Column(String(100), nullable=True)
    created_at: Mapped[DateTime] = Column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    beds: Mapped[List[Bed]] = relationship(
        Bed,
        secondary=bed_group_association_table,
        back_populates="groups",
        lazy="selectin",
    )

    __table_args__ = (Index("ix_unique_bed_group_name", func.lower(name), unique=True),)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "beds": [bed.id for bed in self.beds],
        }


class Observation(Entity):
    __tablename__ = "observations"

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True)
    category: Mapped[str] = Column(String(255), nullable=False, default="vital-signs")
    code: Mapped[str] = Column(String, nullable=False, index=True)
    subject_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    effective_dt: Mapped[datetime] = Column(DateTime(timezone=False), nullable=False)
    value_number: Mapped[Decimal] = Column(DECIMAL, nullable=True)
    value_text: Mapped[str] = Column(String, nullable=True)
    is_alert: Mapped[bool] = Column(Boolean, nullable=False)
    device_primary_identifier: Mapped[str] = Column(String(255), nullable=True)
    device_code: Mapped[str] = Column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "code": self.code,
            "subject_id": self.subject_id,
            "effective_dt": self.effective_dt,
            "value_number": self.value_number,
            "value_text": self.value_text,
            "is_alert": self.is_alert,
        }


class AlertLog(Entity):
    __tablename__ = "alerts_log"
    __mapper_args__ = {"eager_defaults": False}

    __table_args__ = (
        PrimaryKeyConstraint(
            "patient_id", "code", "device_primary_identifier", "determination_time"
        ),
    )

    code: Mapped[str] = Column(String, nullable=False, index=True)
    patient_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_primary_identifier: Mapped[str] = Column(String(255), nullable=True)
    determination_time: Mapped[datetime] = Column(DateTime(timezone=False), nullable=False)
    value_number: Mapped[Decimal] = Column(DECIMAL, nullable=True)
    value_text: Mapped[str] = Column(String, nullable=True)
    device_primary_identifier: Mapped[str] = Column(String, nullable=False)
    device_code: Mapped[str] = Column(String, nullable=True, index=True)
    active: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    trigger_upper_limit: Mapped[float] = Column(Float, nullable=True)
    trigger_lower_limit: Mapped[float] = Column(Float, nullable=True)
    created_at: Mapped[datetime] = Column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def as_dict(self):
        return {
            "code": self.code,
            "active": self.active,
            "value_text": self.value_text,
            "patient_id": self.patient_id,
            "patient_primary_identifier": self.patient_primary_identifier,
            "device_code": self.device_code,
            "determination_time": self.determination_time,
            "device_primary_identifier": self.device_primary_identifier,
            "trigger_upper_limit": self.trigger_upper_limit,
            "trigger_lower_limit": self.trigger_lower_limit,
        }

    def __repr__(self) -> str:
        return (
            f"<AlertLog code={self.code} patient_id={self.patient_id} "
            f"active={self.active} device_primary_identifier={self.device_primary_identifier} "
            f"trigger_upper_limit={self.trigger_upper_limit} "
            f"trigger_lower_limit={self.trigger_lower_limit}>"
        )
