from starlette import status
from users.domain.exceptions import UserProfileNotFoundException

from shared.infrastructure.exceptions.exception_registry import ExceptionMetadata

USERS_EXCEPTION_MAPPINGS = {
    UserProfileNotFoundException: ExceptionMetadata(
        status.HTTP_404_NOT_FOUND, "user_not_found"
    ),
}
