from auth.application.commands.send_mail import SendMailCommand
from auth.domain.events.verification_requested import VerificationRequestedDomainEvent
from shared.application.ports import DomainEventHandler
from shared.infrastructure.cqrs_buses import CommandBus


class SendVerificationMail(DomainEventHandler[VerificationRequestedDomainEvent]):
    def __init__(self, command_bus: CommandBus, base_url: str) -> None:
        self._command_bus = command_bus
        self._base_url = base_url

    async def handle(self, event: VerificationRequestedDomainEvent) -> None:
        recipient = event.email.value
        subject = "Please verify your email address"
        template_name = "verification_mail.html"
        context = {"verification_link": f"{self._base_url}/verify?token={event.token}"}

        cmd = SendMailCommand(
            recipient=recipient,
            subject=subject,
            template_name=template_name,
            context=context,
        )

        await self._command_bus.dispatch(cmd)
