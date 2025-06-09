from abc import ABC, abstractmethod


class EmailService(ABC):
    """Сервис email сообщений-рассылок."""

    @abstractmethod
    async def send_verification_email(self, email: str, code: str) -> None:
        """Отправляет код верефикации на email."""
        pass
