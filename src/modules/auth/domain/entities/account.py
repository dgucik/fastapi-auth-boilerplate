from dataclasses import dataclass, field
from uuid import UUID

from auth.domain.events.account_registered import AccountRegisteredDomainEvent
from auth.domain.events.password_changed import PasswordChangedDomainEvent
from auth.domain.events.password_reset_completed import (
    PasswordResetCompletedDomainEvent,
)
from auth.domain.events.password_reset_requested import (
    PasswordResetRequestedDomainEvent,
)
from auth.domain.events.verification_requested import VerificationRequestedDomainEvent
from auth.domain.exceptions import (
    AccountAlreadyVerifiedException,
    AccountNotVerifiedException,
    InvalidPasswordException,
)
from auth.domain.ports import PasswordHasher
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.plain_password import PlainPassword
from shared.domain.primitives import AggregateRoot


@dataclass
class Account(AggregateRoot):
    """Account domain entity representing a user.

    Attributes:
        email: User's email address.
        id: Unique identifier.
        is_verified: Whether email is verified.
        is_superuser: Whether user has admin privileges.
    """

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
        """Factory method to create a new Account.

        Args:
            id: Unique identifier.
            email: Email address.
            plain_password: Password to set.
            hasher: Service to hash the password.

        Returns:
            New Account instance.
        """
        new_account = cls(id=id, email=email)
        new_account.set_password(plain_password, hasher)

        new_account.add_event(
            AccountRegisteredDomainEvent(
                account_id=new_account.id, email=new_account.email
            )
        )

        return new_account

    def set_password(
        self, plain_password: PlainPassword, hasher: PasswordHasher
    ) -> None:
        """Sets the account password.

        Args:
            plain_password: New password.
            hasher: Hashing service.
        """
        self._password_hash = hasher.hash(plain_password.value)

    def login(self, plain_password: PlainPassword, hasher: PasswordHasher) -> None:
        """Authenticates the user.

        Args:
            plain_password: Password attempt.
            hasher: Hashing service for verification.

        Raises:
            InvalidPasswordException: If password doesn't match.
            AccountNotVerifiedException: If account is not verified.
        """
        if not hasher.verify(plain_password.value, self._password_hash):
            raise InvalidPasswordException

        if not self.is_verified:
            raise AccountNotVerifiedException

    def verify_email(self) -> None:
        """Marks the email as verified.

        Raises:
            AccountAlreadyVerifiedException: If already verified.
        """
        if self.is_verified:
            raise AccountAlreadyVerifiedException()
        self.is_verified = True

    def request_verification(self, token: str) -> None:
        """Initiates email verification process.

        Args:
            token: Verification token to send.

        Raises:
            AccountAlreadyVerifiedException: If already verified.
        """
        if self.is_verified:
            raise AccountAlreadyVerifiedException()
        self.add_event(
            VerificationRequestedDomainEvent(
                account_id=self.id, email=self.email, token=token
            )
        )

    def request_password_reset(self, token: str) -> None:
        """Initiates password reset process.

        Args:
            token: Reset token to send.
        """
        self.add_event(
            PasswordResetRequestedDomainEvent(
                account_id=self.id, email=self.email, token=token
            )
        )

    def reset_password(
        self, new_password: PlainPassword, hasher: PasswordHasher
    ) -> None:
        """Resets the password.

        Args:
            new_password: New password.
            hasher: Hashing service.
        """
        self.set_password(new_password, hasher)
        self.add_event(PasswordResetCompletedDomainEvent(account_id=self.id))

    def change_password(
        self,
        old_password: PlainPassword,
        new_password: PlainPassword,
        hasher: PasswordHasher,
    ) -> None:
        """Changes the password.

        Args:
            old_password: Current password.
            new_password: New password.
            hasher: Hashing service.

        Raises:
            InvalidPasswordException: If old password is incorrect.
        """
        if not hasher.verify(old_password.value, self._password_hash):
            raise InvalidPasswordException()

        self.set_password(new_password, hasher)

        self.add_event(PasswordChangedDomainEvent(account_id=self.id))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Account):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
