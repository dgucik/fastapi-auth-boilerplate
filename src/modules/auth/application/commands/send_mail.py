import logging
from dataclasses import dataclass
from typing import Any

from auth.domain.interfaces import MailSender
from shared.application.ports import Command, Handler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SendMailCommand(Command):
    recipient: str
    subject: str
    template_name: str
    context: dict[str, Any]


class SendMailHandler(Handler[SendMailCommand, None]):
    def __init__(self, mail_sender: MailSender) -> None:
        self._mail_sender = mail_sender

    async def handle(self, command: SendMailCommand) -> None:
        await self._mail_sender.send(
            recipient=command.recipient,
            subject=command.subject,
            template_name=command.template_name,
            context=command.context,
        )
        logger.info(f"Email: {command.subject} sent to: {command.recipient}.")
