from auth.domain.events import VerificationRequested
from auth.domain.interfaces import MailSender, TokenManager
from shared.application.event_handling import DomainEventHandler


class SendVerificationMail(DomainEventHandler[VerificationRequested]):
    is_async = True

    def __init__(
        self, token_manager: TokenManager, mail_sender: MailSender, base_url: str
    ) -> None:
        self._token_manager = token_manager
        self._mail_sender = mail_sender
        self._base_url = base_url

    async def handle(self, event: VerificationRequested) -> None:
        token = self._token_manager.create_verification_token(
            subject=str(event.account_id)
        )
        verification_link = f"{self._base_url}/verify?token={token}"
        subject = "Please verify your email address"

        await self._mail_sender.send_mail(
            recipients=[event.email.value],
            subject=subject,
            verification_link=verification_link,
            verification_token_expires_in_minutes=self._token_manager.verification_token_expires_in_minutes,
        )
