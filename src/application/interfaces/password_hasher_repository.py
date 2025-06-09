from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Интерфейс утилиты для хеширования и верефикации пароля."""

    @abstractmethod
    async def get_password_hash(self, password: str) -> str:
        """Хеширует пароль."""
        pass

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет соответствие введенного пароля сохраненному хешу."""
        pass
