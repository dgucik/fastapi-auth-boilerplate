from starlette import status

from auth.application.exceptions import PasswordsDoNotMatchException
from auth.domain.exceptions import InvalidPasswordException
from shared.infrastructure.exceptions.exception_registry import ExceptionMetadata

AUTH_EXCEPTION_MAPPINGS = {
    InvalidPasswordException: ExceptionMetadata(
        status.HTTP_401_UNAUTHORIZED, "invalid_password"
    ),
    PasswordsDoNotMatchException: ExceptionMetadata(
        status.HTTP_400_BAD_REQUEST, "password_do_not_match"
    ),
}
