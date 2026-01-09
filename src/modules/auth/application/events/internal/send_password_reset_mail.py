import logging

from auth.domain.events.password_reset_requested import (
    PasswordResetRequestedDomainEvent,
)
from auth.domain.ports import MailSender
from shared.application.ports import DomainEventHandler

logger = logging.getLogger(__name__)


class SendPasswordResetMailHandler(
    DomainEventHandler[PasswordResetRequestedDomainEvent]
):
    def __init__(self, command_bus: MailSender, base_url: str) -> None:
        self._mail_sender = command_bus
        self._base_url = base_url

    async def handle(self, event: PasswordResetRequestedDomainEvent) -> None:
        recipient = event.email.value
        subject = "Reset your password"
        template_name = "reset_password_mail.html"
        context = {"reset_link": f"{self._base_url}/reset-password?token={event.token}"}

        await self._mail_sender.send(
            recipient=recipient,
            subject=subject,
            template_name=template_name,
            context=context,
        )
        logger.info(f"Email: {subject} sent to: {recipient}.")
