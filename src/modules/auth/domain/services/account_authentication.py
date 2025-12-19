from dataclasses import dataclass

from auth.domain.exceptions import InvalidPasswordException
from auth.domain.interfaces import PasswordHasher, TokenManager
from auth.domain.repositories import AccountRepository
from auth.domain.value_objects import Email, PlainPassword


@dataclass(frozen=True)
class AuthenticationResponse:
    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int


class AccountAuthenticationService:
    def __init__(self, hasher: PasswordHasher, token_manager: TokenManager) -> None:
        self._hasher = hasher
        self._token_manager = token_manager

    async def authenticate(
        self, repo: AccountRepository, email: Email, plain_password: PlainPassword
    ) -> AuthenticationResponse:
        account = await repo.get_by_email(email)

        if not account:
            raise InvalidPasswordException

        account.login(plain_password, self._hasher)

        access_token = self._token_manager.create_access_token(subject=str(account.id))
        refresh_token = self._token_manager.create_refresh_token(
            subject=str(account.id)
        )
        refresh_token_expires_in_seconds = (
            self._token_manager.refresh_token_expires_in_seconds
        )

        return AuthenticationResponse(
            access_token, refresh_token, refresh_token_expires_in_seconds
        )
