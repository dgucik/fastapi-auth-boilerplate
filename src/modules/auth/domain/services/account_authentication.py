from auth.domain.exceptions import InvalidPasswordException
from auth.domain.ports import AuthenticationResult, PasswordHasher, TokenManager
from auth.domain.repositories import AccountRepository
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.plain_password import PlainPassword


class AccountAuthenticationService:
    def __init__(self, hasher: PasswordHasher, token_manager: TokenManager) -> None:
        self._hasher = hasher
        self._token_manager = token_manager

    async def authenticate(
        self, repo: AccountRepository, email: Email, plain_password: PlainPassword
    ) -> AuthenticationResult:
        account = await repo.get_by_email(email)

        if not account:
            raise InvalidPasswordException

        account.login(plain_password, self._hasher)

        return self._token_manager.issue_auth_tokens(str(account.id))
