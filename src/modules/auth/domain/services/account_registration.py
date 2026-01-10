from uuid import UUID

from auth.domain.entities.account import Account
from auth.domain.exceptions import EmailAlreadyExistsException
from auth.domain.ports import PasswordHasher
from auth.domain.repositories import AccountRepository
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.plain_password import PlainPassword


class AccountRegistrationService:
    """Domain service for account registration."""

    def __init__(self, hasher: PasswordHasher):
        self._hasher = hasher

    async def register(
        self,
        repo: AccountRepository,
        account_id: UUID,
        email: Email,
        password: PlainPassword,
    ) -> Account:
        """Registers a new account.

        Args:
            repo: Account repository.
            account_id: New account ID.
            email: New account email.
            password: New account password.

        Returns:
            The created Account entity.

        Raises:
            EmailAlreadyExistsException: If email is taken.
        """
        if await repo.get_by_email(email):
            raise EmailAlreadyExistsException

        return Account.create(
            id=account_id, email=email, plain_password=password, hasher=self._hasher
        )
