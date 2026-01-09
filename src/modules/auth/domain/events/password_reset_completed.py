from dataclasses import dataclass
from typing import Any
from uuid import UUID

from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class PasswordResetCompletedDomainEvent(DomainEvent):
    account_id: UUID

    def to_dict(self) -> dict[str, Any]:
        return {"account_id": str(self.account_id)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PasswordResetCompletedDomainEvent":
        return cls(account_id=UUID(data["account_id"]))
