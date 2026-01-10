from auth.domain.repositories import AccountRepository
from shared.application.ports import UnitOfWork


class AuthUnitOfWork(UnitOfWork):
    """Unit of Work for the Auth module."""

    accounts: AccountRepository
