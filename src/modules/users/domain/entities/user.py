from dataclasses import dataclass
from uuid import UUID

from users.domain.value_objects.username import Username

from shared.domain.primitives import AggregateRoot


@dataclass
class User(AggregateRoot):
    account_id: UUID
    username: Username
    id: UUID

    @classmethod
    def create(cls, id: UUID, account_id: UUID, username: Username) -> "User":
        return cls(id=id, account_id=account_id, username=username)
