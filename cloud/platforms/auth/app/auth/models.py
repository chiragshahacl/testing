import uuid
from typing import Any

from sqlalchemy import UUID, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models import Base, Entity

role_permission_association = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", UUID, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_id", UUID, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    ),
)

user_role_association = Table(
    "user_role",
    Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id"), primary_key=True),
    Column("role_id", UUID, ForeignKey("roles.id"), primary_key=True),
)


class User(Entity):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    # relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=user_role_association,
        back_populates="users",
        lazy="joined",
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "roles": [role.as_dict() for role in self.roles],
        }


class Role(Entity):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    # relationships
    users = relationship(
        "User",
        secondary=user_role_association,
        back_populates="roles",
    )
    permissions = relationship(
        "Permission",
        secondary=role_permission_association,
        back_populates="roles",
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
        }


class Permission(Entity):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_permission_association,
        back_populates="permissions",
    )
