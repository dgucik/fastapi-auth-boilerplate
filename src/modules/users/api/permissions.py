# ruff: noqa: B008

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Depends
from users.api.dependencies import get_current_account_from_header

from auth.contracts.dtos import AuthAccountDto
from shared.infrastructure.exceptions.exceptions import PermissionDeniedException


def require_superuser() -> Callable[..., Coroutine[Any, Any, None]]:
    async def _permission(
        account: AuthAccountDto = Depends(get_current_account_from_header),
    ) -> None:
        if not account.is_superuser:
            raise PermissionDeniedException()

    return _permission
