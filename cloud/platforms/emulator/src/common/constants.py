import enum

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"
