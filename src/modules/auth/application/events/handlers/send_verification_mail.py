import logging

from auth.domain.events import VerificationRequestedDomainEvent
from auth.domain.interfaces import MailSender
from shared.application.ports import DomainEventHandler

logger = logging.getLogger(__name__)


class SendVerificationMail(DomainEventHandler[VerificationRequestedDomainEvent]):
    def __init__(self, mail_sender: MailSender, base_url: str) -> None:
        self._mail_sender = mail_sender
        self._base_url = base_url

    async def handle(self, event: VerificationRequestedDomainEvent) -> None:
        subject = "Please verify your email address"
        template_name = "verification_mail.html"
        context = {"verification_link": f"{self._base_url}/verify?token={event.token}"}

        await self._mail_sender.send(
            recipient=event.email.value,
            subject=subject,
            template_name=template_name,
            context=context,
        )
        logger.info(f"Verification mail enqueued for: {event.email.value}")
