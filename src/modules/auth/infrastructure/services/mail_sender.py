import logging
import os
from email.message import EmailMessage
from typing import Any

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from auth.domain.interfaces import (
    MailSender,
)
from config.env import MailSettings

logger = logging.getLogger(__name__)


class AioSmtpMailSender(MailSender):
    def __init__(self, config: MailSettings | dict[str, Any]) -> None:
        if isinstance(config, dict):
            self._config = MailSettings(**config)
        else:
            self._config = config

        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, "templates")

        self._jinja_env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send(
        self, recipient: str, subject: str, template_name: str, context: dict[str, Any]
    ) -> None:
        template = self._jinja_env.get_template(template_name)

        html_content = template.render(**context)

        message = EmailMessage()
        message["From"] = self._config.FROM
        message["To"] = recipient
        message["Subject"] = subject
        message.add_alternative(html_content, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=self._config.SERVER,
            port=self._config.PORT,
            username=self._config.USERNAME,
            password=self._config.PASSWORD,
            use_tls=False,
            start_tls=True,
        )
        logger.info(f"Email sent to {recipient}: {subject}")
