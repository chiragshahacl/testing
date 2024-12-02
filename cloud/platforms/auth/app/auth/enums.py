import enum


class RoleNames(str, enum.Enum):
    ADMIN = "admin"
    TECH = "tech"
    CLINICAL = "clinical"
    ORGANIZATION = "organization"
