from dataclasses import dataclass
from uuid import UUID

from users.domain.value_objects.username import Username

from shared.domain.primitives import AggregateRoot


@dataclass
class User(AggregateRoot):
    """User aggregate root entity.

    Attributes:
        account_id: Associated account UUID.
        username: User's username value object.
        id: User UUID.
    """

    account_id: UUID
    username: Username
    id: UUID

    @classmethod
    def create(cls, id: UUID, account_id: UUID, username: Username) -> "User":
        """Factory method to create a new User.

        Args:
            id: User UUID.
            account_id: Account UUID.
            username: Username value object.

        Returns:
            User: New User instance.
        """
        return cls(id=id, account_id=account_id, username=username)

    def change_username(self, new_username: Username) -> None:
        """Changes the user's username.

        Args:
            new_username: New Username value object.
        """
        self.username = new_username

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
