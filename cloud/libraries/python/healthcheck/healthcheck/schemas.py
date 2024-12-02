from dataclasses import dataclass
from datetime import datetime


@dataclass
class HealthcheckRecord:
    timestamp: datetime
