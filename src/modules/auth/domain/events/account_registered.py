from dataclasses import dataclass
from typing import Any
from uuid import UUID

from auth.domain.value_objects.email import Email
from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class AccountRegisteredDomainEvent(DomainEvent):
    account_id: UUID
    email: Email

    def to_dict(self) -> dict[str, Any]:
        return {"account_id": str(self.account_id), "email": self.email.value}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccountRegisteredDomainEvent":
        return cls(account_id=UUID(data["account_id"]), email=Email(data["email"]))
