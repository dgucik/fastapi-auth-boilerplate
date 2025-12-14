from uuid import UUID

from auth.domain.account import Account, Email, PlainPassword
from auth.domain.exceptions import EmailAlreadyExistsException
from auth.domain.interfaces import PasswordHasher
from auth.domain.repositories import AccountRepository


class AccountRegistrationService:
    def __init__(self, hasher: PasswordHasher):
        self._hasher = hasher

    async def register(
        self,
        repository: AccountRepository,
        id: UUID,
        email: Email,
        password: PlainPassword,
    ) -> Account:
        if await repository.get_by_email(email):
            raise EmailAlreadyExistsException

        return Account.create(
            id=id, email=email, plain_password=password, hasher=self._hasher
        )
