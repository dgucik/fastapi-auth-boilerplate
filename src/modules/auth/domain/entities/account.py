from dataclasses import dataclass, field
from uuid import UUID

from auth.domain.events import AccountRegistered
from auth.domain.exceptions import AccountNotVerifiedException, InvalidPasswordException
from auth.domain.interfaces import PasswordHasher
from auth.domain.value_objects import Email, PlainPassword
from shared.domain.primitives import AggregateRoot


@dataclass
class Account(AggregateRoot):
    email: Email
    id: UUID
    _password_hash: str = field(default="", repr=False)
    is_verified: bool = False
    is_superuser: bool = False

    @classmethod
    def create(
        cls,
        id: UUID,
        email: Email,
        plain_password: PlainPassword,
        hasher: PasswordHasher,
    ) -> "Account":
        new_account = cls(id=id, email=email)
        new_account.set_password(plain_password, hasher)

        new_account._events.append(
            AccountRegistered(account_id=new_account.id, email=new_account.email)
        )

        return new_account

    def set_password(
        self, plain_password: PlainPassword, hasher: PasswordHasher
    ) -> None:
        self._password_hash = hasher.hash(plain_password.value)

    def login(self, plain_password: PlainPassword, hasher: PasswordHasher) -> None:
        if not hasher.verify(plain_password.value, self._password_hash):
            raise InvalidPasswordException

        if not self.is_verified:
            raise AccountNotVerifiedException

    def verify_email(self) -> None:
        if self.is_verified:
            return
        self.is_verified = True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Account):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
