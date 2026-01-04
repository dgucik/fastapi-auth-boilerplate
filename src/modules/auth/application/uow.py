from auth.domain.repositories import AccountRepository
from shared.application.ports import UnitOfWork


class AuthUnitOfWork(UnitOfWork):
    accounts: AccountRepository
