import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent(ABC):
    event_id: uuid.UUID = field(default_factory=uuid.uuid4, init=False)
    occurred_at: datetime = field(default_factory=datetime.utcnow, init=False)
