from dataclasses import dataclass
from typing import Any
from uuid import UUID

from shared.application.ports import IntegrationEvent


@dataclass(frozen=True)
class AccountRegisteredIntegrationEvent(IntegrationEvent):
    account_id: UUID
    topic: str

    def to_dict(self) -> dict[str, Any]:
        data = {}
        data["account_id"] = str(self.account_id)
        data["topic"] = self.topic
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccountRegisteredIntegrationEvent":
        data["account_id"] = UUID(data["account_id"])
        data["topic"] = data["topic"]
        return cls(**data)
