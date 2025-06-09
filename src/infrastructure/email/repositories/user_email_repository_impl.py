# Репозиторий для отправки email
from src.application.interfaces.email_service import EmailService
from aiosmtplib import SMTPException
from email.mime.text import MIMEText
from pydantic import EmailStr
import logging
from src.infrastructure.email.email_client_manager import SMTPClientManager

logger = logging.getLogger(__name__)


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class EmailServiceImpl(EmailService):
    """Репозиторий для отправки email сообщений."""

    def __init__(self, smtp_client_manager: SMTPClientManager) -> None:
        self._smtp_client_manager = smtp_client_manager

    async def send_verification_email(self, to_email: EmailStr, code: str) -> None:
        """Отправляет код верификации на email."""
        await self._smtp_client_manager.ensure_connected()

        msg = MIMEText(f"Your verification code is: {code}")
        msg["Subject"] = "Email Verification Code"
        msg["From"] = self._smtp_client_manager._smtp_config.user
        msg["To"] = to_email

        try:
            await self._smtp_client_manager.client.send_message(msg)
            logger.info(f"Verification email sent to {to_email} with code {code}")
        except SMTPException as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while sending email to {to_email}: {e}")
            raise
