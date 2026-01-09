from uuid import UUID

from users.domain.entities.user import User
from users.domain.exceptions import (
    UserAlreadyExistsForAccountException,
    UsernameIsAlreadyTakenException,
)
from users.domain.repositories import UserRepository
from users.domain.value_objects.username import Username


class UserCreationService:
    async def create_user(
        self,
        repository: UserRepository,
        user_id: UUID,
        account_id: UUID,
        username: Username,
    ) -> User:
        if await repository.get_by_username(username):
            raise UsernameIsAlreadyTakenException

        if await repository.get_by_id(account_id):
            raise UserAlreadyExistsForAccountException

        return User.create(id=user_id, account_id=account_id, username=username)
