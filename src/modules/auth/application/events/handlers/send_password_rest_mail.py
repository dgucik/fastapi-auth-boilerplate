from auth.domain.events import PasswordResetRequestedDomainEvent
from auth.domain.interfaces import MailSender
from shared.application.event_handling import DomainEventHandler


class SendPasswordResetMail(DomainEventHandler[PasswordResetRequestedDomainEvent]):
    def __init__(self, mail_sender: MailSender, base_url: str) -> None:
        self._mail_sender = mail_sender
        self._base_url = base_url

    async def handle(self, event: PasswordResetRequestedDomainEvent) -> None:
        reset_link = f"{self._base_url}/reset-password?token={event.token}"
        subject = "Reset your password"
        await self._mail_sender.send_reset_link_mail(
            recipient=event.email.value,
            subject=subject,
            reset_link=reset_link,
        )
