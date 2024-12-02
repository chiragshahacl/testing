"""
Add basic roles and permissions
"""

import uuid

from alembic import op
from sqlalchemy import UUID, Column, ForeignKey, String, Table, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

revision = "704b9ed54608"
down_revision = "43fdc498fde1"
branch_labels = None
depends_on = None


# Define the roles and permissions you want to create
ROLES_TO_CREATE = [
    {"name": "admin"},
    {"name": "tech"},
    {"name": "clinical"},
    {"name": "organization"},
]

PERMISSIONS_TO_CREATE = [{"name": "read"}, {"name": "write"}, {"name": "delete"}]


Base = declarative_base()

role_permission_association = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", UUID, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", UUID, ForeignKey("permissions.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    permissions = relationship(
        "Permission", secondary=role_permission_association, back_populates="roles"
    )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # relationships
    roles: Mapped["Role"] = relationship(
        "Role", secondary=role_permission_association, back_populates="permissions"
    )


def upgrade() -> None:
    session = Session(bind=op.get_bind())

    permissions = [Permission(id=uuid.uuid4(), **p) for p in PERMISSIONS_TO_CREATE]
    session.add_all(permissions)
    session.flush()

    roles = [Role(id=uuid.uuid4(), **r) for r in ROLES_TO_CREATE]
    session.add_all(roles)
    session.flush()

    for role in roles:
        role.permissions = permissions
        session.add(role)
        session.flush()

    session.commit()


def downgrade() -> None:
    session = Session(bind=op.get_bind())

    stmt = delete(role_permission_association)
    session.execute(stmt)
    session.flush()

    stmt = delete(Role)
    session.execute(stmt)
    session.flush()

    stmt = delete(Permission)
    session.execute(stmt)
    session.flush()
    session.commit()
