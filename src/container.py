from collections.abc import Callable
from typing import Any

from dependency_injector import containers, providers

from auth import AuthContainer


class AppContainer(containers.DeclarativeContainer):
    settings = providers.Configuration()

    session_factory: providers.Provider[Callable[..., Any]] = providers.Dependency()

    # Containers for different modules
    auth = providers.Container(
        AuthContainer, settings=settings, session_factory=session_factory
    )
