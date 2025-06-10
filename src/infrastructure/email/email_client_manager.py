import logging
from typing import Optional

from aiosmtplib import SMTP, SMTPException

from src.config import settings

logger = logging.getLogger(__name__)


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class SMTPClientManager:
    """Класс для управления соединением с SMTP сервером."""

    def __init__(self) -> None:
        self._smtp_config = settings.smtp
        self._client: Optional[SMTP] = None

    async def connect(self) -> None:
        """Инициализация SMTP клиента."""
        try:
            self._client = SMTP(
                hostname=self._smtp_config.server,
                port=self._smtp_config.port,
                start_tls=True,
            )
            await self._client.connect()
            await self._client.login(self._smtp_config.user, self._smtp_config.password)
            logger.info("Successfully connected to SMTP server.")
        except SMTPException as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            raise

    async def disconnect(self) -> None:
        """Закрытие соединения с SMTP сервером."""
        if self._client and self._client.is_connected:
            await self._client.quit()
            self._client = None
            logger.info("Disconnected from SMTP server.")

    async def ensure_connected(self) -> None:
        """Проверяет и, при необходимости, восстанавливает соединение."""
        if not self._client or not self._client.is_connected:
            await self.connect()

    @property
    def client(self) -> Optional[SMTP]:
        """Возвращает текущий SMTP клиент."""
        return self._client


EmailClietn = SMTPClientManager()
