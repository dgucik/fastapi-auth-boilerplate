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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
