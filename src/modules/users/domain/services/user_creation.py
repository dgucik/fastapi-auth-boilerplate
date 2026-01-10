from uuid import UUID

from users.domain.entities.user import User
from users.domain.exceptions import (
    UserAlreadyExistsForAccountException,
    UsernameIsAlreadyTakenException,
)
from users.domain.repositories import UserRepository
from users.domain.value_objects.username import Username


class UserCreationService:
    """Domain service for handling user creation rules."""

    async def create_user(
        self,
        repository: UserRepository,
        user_id: UUID,
        account_id: UUID,
        username: Username,
    ) -> User:
        """Creates a new user ensuring domain rules.

        Args:
            repository: User repository to check uniqueness.
            user_id: New User UUID.
            account_id: Associated Account UUID.
            username: Desired Username.

        Returns:
            User: Created User entity.

        Raises:
            UsernameIsAlreadyTakenException: If username is taken.
            UserAlreadyExistsForAccountException: If account already has a user profile.
        """
        if await repository.get_by_username(username):
            raise UsernameIsAlreadyTakenException

        if await repository.get_by_id(account_id):
            raise UserAlreadyExistsForAccountException

        return User.create(id=user_id, account_id=account_id, username=username)
