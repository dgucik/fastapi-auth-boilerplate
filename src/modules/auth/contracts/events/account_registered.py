from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from shared.application.ports import IntegrationEvent


@dataclass(frozen=True)
class AccountRegisteredIntegrationEvent(IntegrationEvent):
    account_id: UUID
    TOPIC: str = field(default="account.registered", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {"account_id": str(self.account_id)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccountRegisteredIntegrationEvent":
        return cls(account_id=UUID(data["account_id"]))
