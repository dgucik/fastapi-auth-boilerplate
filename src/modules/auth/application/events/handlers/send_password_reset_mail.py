from auth.application.commands.send_mail import SendMailCommand
from auth.domain.events.password_reset_requested import (
    PasswordResetRequestedDomainEvent,
)
from shared.application.ports import DomainEventHandler
from shared.infrastructure.cqrs_buses import CommandBus


class SendPasswordResetMail(DomainEventHandler[PasswordResetRequestedDomainEvent]):
    def __init__(self, command_bus: CommandBus, base_url: str) -> None:
        self._command_bus = command_bus
        self._base_url = base_url

    async def handle(self, event: PasswordResetRequestedDomainEvent) -> None:
        recipient = event.email.value
        subject = "Reset your password"
        template_name = "reset_password_mail.html"
        context = {"reset_link": f"{self._base_url}/reset-password?token={event.token}"}

        cmd = SendMailCommand(
            recipient=recipient,
            subject=subject,
            template_name=template_name,
            context=context,
        )

        await self._command_bus.dispatch(cmd)
