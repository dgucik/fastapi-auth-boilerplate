from dataclasses import dataclass
from typing import Any
from uuid import UUID

from auth.domain.value_objects import Email
from shared.domain.events import Event


@dataclass(frozen=True)
class AccountRegistered(Event):
    account_id: UUID
    email: Email

    def to_dict(self) -> dict[str, Any]:
        data = {}
        data["account_id"] = str(self.account_id)
        data["email"] = self.email.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccountRegistered":
        data["account_id"] = UUID(data["account_id"])
        data["email"] = Email(data["email"])
        return cls(**data)


@dataclass(frozen=True)
class VerificationRequested(Event):
    account_id: UUID
    email: Email

    def to_dict(self) -> dict[str, Any]:
        data = {}
        data["account_id"] = str(self.account_id)
        data["email"] = self.email.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VerificationRequested":
        data["account_id"] = UUID(data["account_id"])
        data["email"] = Email(data["email"])
        return cls(**data)
