import enum


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class HL7GenderEnum(str, enum.Enum):
    MALE = "M"
    FEMALE = "F"
    AMBIGUOUS = "A"
    NOT_APPLICABLE = "N"
    OTHER = "O"
    UNKNOWN = "U"
