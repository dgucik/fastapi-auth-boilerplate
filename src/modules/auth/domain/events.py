from dataclasses import dataclass
from uuid import UUID

from auth.domain.value_objects import Email
from shared.domain.events import DomainEvent


@dataclass(frozen=True)
class AccountRegistered(DomainEvent):
    account_id: UUID
    email: Email


@dataclass(frozen=True)
class VerificationRequested(DomainEvent):
    account_id: UUID
    email: Email
