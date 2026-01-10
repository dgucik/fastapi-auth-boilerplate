from dependency_injector import containers, providers

from auth.infrastructure.services.mail_sender import AioSmtpMailSender
from auth.infrastructure.services.password_hasher import BcryptPasswordHasher
from auth.infrastructure.services.token_manager import JWTTokenManager


class InfraServicesContainer(containers.DeclarativeContainer):
    """Container for infrastructure services."""

    settings = providers.Configuration()

    hasher = providers.Singleton(BcryptPasswordHasher)

    token_manager = providers.Singleton(
        JWTTokenManager,
        secret_key=settings.token.SECRET_KEY,
        algorithm=settings.token.ALGORITHM,
        access_expire_minutes=settings.token.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expire_days=settings.token.REFRESH_TOKEN_EXPIRE_DAYS,
        verification_expire_minutes=settings.token.VERIFICATION_TOKEN_EXPIRE_MINUTES,
        password_reset_expire_minutes=settings.token.PASSWORD_RESET_EXPIRE_MINUTES,
    )

    mail_sender = providers.Singleton(AioSmtpMailSender, config=settings.mail)
