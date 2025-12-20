from auth.domain.events import VerificationRequestedDomainEvent
from auth.domain.interfaces import MailSender, TokenManager
from shared.application.event_handling import DomainEventHandler


class SendVerificationMail(DomainEventHandler[VerificationRequestedDomainEvent]):
    def __init__(
        self, token_manager: TokenManager, mail_sender: MailSender, base_url: str
    ) -> None:
        self._token_manager = token_manager
        self._mail_sender = mail_sender
        self._base_url = base_url

    async def handle(self, event: VerificationRequestedDomainEvent) -> None:
        verification_link = f"{self._base_url}/verify?token={event.token}"
        subject = "Please verify your email address"
        await self._mail_sender.send_mail(
            recipients=["danielgucik7@gmail.com"],
            subject=subject,
            verification_link=verification_link,
        )
