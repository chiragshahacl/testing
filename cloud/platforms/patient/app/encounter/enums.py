from enum import Enum


class EncounterStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
