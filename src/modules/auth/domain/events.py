from dataclasses import dataclass
from typing import Any
from uuid import UUID

from auth.domain.value_objects import Email
from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class AccountRegisteredDomainEvent(DomainEvent):
    account_id: UUID
    email: Email

    def to_dict(self) -> dict[str, Any]:
        data = {}
        data["account_id"] = str(self.account_id)
        data["email"] = self.email.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccountRegisteredDomainEvent":
        data["account_id"] = UUID(data["account_id"])
        data["email"] = Email(data["email"])
        return cls(**data)


@dataclass(frozen=True)
class VerificationRequestedDomainEvent(DomainEvent):
    account_id: UUID
    email: Email

    def to_dict(self) -> dict[str, Any]:
        data = {}
        data["account_id"] = str(self.account_id)
        data["email"] = self.email.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VerificationRequestedDomainEvent":
        data["account_id"] = UUID(data["account_id"])
        data["email"] = Email(data["email"])
        return cls(**data)
