from users.domain.repositories import UserRepository

from shared.application.ports import UnitOfWork


class UsersUnitOfWork(UnitOfWork):
    users: UserRepository
