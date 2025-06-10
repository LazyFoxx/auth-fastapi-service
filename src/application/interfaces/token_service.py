from abc import ABC, abstractmethod


class TokenService(ABC):
    """Интерфейс (порт) для работы с токенами."""

    @abstractmethod
    async def generate_token(self, email: str) -> str:
        """генерирует уникальный токен по email."""

    @abstractmethod
    async def create_access_token(self, data: dict) -> str:
        """генерирует jwt access token."""

    @abstractmethod
    async def create_refresh_token(self, data: dict) -> str:
        """генерирует jwt refresh token."""

    @abstractmethod
    async def verify_token(self, token: str) -> dict:
        """Декодирует jwt и возвращает payload."""
