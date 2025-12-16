from auth.domain.repositories import AccountRepository
from shared.application.uow import UnitOfWork


class AuthUnitOfWork(UnitOfWork):
    accounts: AccountRepository | None
