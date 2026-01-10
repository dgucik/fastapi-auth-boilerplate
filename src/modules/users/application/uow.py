from users.domain.repositories import UserRepository

from shared.application.ports import UnitOfWork


class UsersUnitOfWork(UnitOfWork):
    """Unit of Work for the Users module.

    Attributes:
        users: Repository for User entities.
    """

    users: UserRepository
