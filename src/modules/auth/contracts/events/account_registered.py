from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from shared.application.ports import IntegrationEvent


@dataclass(frozen=True)
class AccountRegisteredIntegrationEvent(IntegrationEvent):
    """Integration event published when an account is registered."""

    account_id: UUID
    TOPIC: str = field(default="account.registered", init=False)

    def to_dict(self) -> dict[str, Any]:
        """Serializes event to dictionary."""
        return {"account_id": str(self.account_id)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccountRegisteredIntegrationEvent":
        """Deserializes event from dictionary."""
        return cls(account_id=UUID(data["account_id"]))
