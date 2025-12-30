from auth.domain.events import PasswordResetRequestedDomainEvent
from auth.domain.interfaces import MailSender
from shared.application.event_handling import DomainEventHandler


class SendPasswordResetMail(DomainEventHandler[PasswordResetRequestedDomainEvent]):
    def __init__(self, mail_sender: MailSender, base_url: str) -> None:
        self._mail_sender = mail_sender
        self._base_url = base_url

    async def handle(self, event: PasswordResetRequestedDomainEvent) -> None:
        subject = "Reset your password"
        template_name = "reset_password_mail.html"
        context = {"reset_link": f"{self._base_url}/reset-password?token={event.token}"}

        await self._mail_sender.send(
            recipient=event.email.value,
            subject=subject,
            template_name=template_name,
            context=context,
        )
