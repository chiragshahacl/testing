from datetime import datetime

from pydantic import BaseModel, Field


class MLLPMessage(BaseModel):
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
