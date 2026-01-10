from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class PasswordHasher(ABC):
    """Interface for password hashing services."""

    @abstractmethod
    def hash(self, password: str) -> str:
        """Hashes the password."""
        pass

    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool:
        """Verifies if plain password matches hashed."""
        pass


class TokenScope(StrEnum):
    """Enumeration of token scopes."""

    ACCESS = "access"
    REFRESH = "refresh"
    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"  # noqa: S105


@dataclass(frozen=True)
class AuthenticationResult:
    """Result of an authentication attempt."""

    access_token: str
    refresh_token: str
    refresh_token_expires_in_seconds: int


class TokenManager(ABC):
    """Interface for token management."""

    @abstractmethod
    def issue_auth_tokens(self, subject: str) -> AuthenticationResult:
        """Issues access and refresh tokens."""
        pass

    @abstractmethod
    def create_access_token(self, subject: str) -> str:
        """Creates a new access token."""
        pass

    @abstractmethod
    def create_refresh_token(self, subject: str) -> str:
        """Creates a new refresh token."""
        pass

    @abstractmethod
    def create_verification_token(self, subject: str) -> str:
        """Creates a verification token."""
        pass

    @abstractmethod
    def create_password_reset_token(self, subject: str) -> str:
        """Creates a password reset token."""
        pass

    @abstractmethod
    def decode_token(self, token: str, expected_type: TokenScope) -> str:
        """Decodes and validates a token, returning the subject."""
        pass

    @property
    @abstractmethod
    def refresh_token_expires_in_seconds(self) -> int:
        """Returns refresh token expiration time in seconds."""
        pass

    @property
    @abstractmethod
    def verification_token_expires_in_minutes(self) -> int:
        """Returns verification token expiration time in minutes."""
        pass


class MailSender(ABC):
    """Interface for sending emails."""

    @abstractmethod
    async def send(
        self, recipient: str, subject: str, template_name: str, context: dict[str, Any]
    ) -> None:
        """Sends an email."""
        pass
