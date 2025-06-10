from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.user import User as DomainUser


class UserCacheRepository(ABC):
    """Интерфейс (порт) для работы с кэшем пользователей."""

    @abstractmethod
    async def get(self, key: str) -> Optional[DomainUser]:
        """Получить пользователя из кэша по ключу."""
        pass

    @abstractmethod
    async def save(self, key: str, user: DomainUser, ttl: int):
        """Сохранить пользователя в кэше по ключу с указанным временем жизни (TTL)."""
        pass

    @abstractmethod
    async def delete(self, key: str):
        """Удалить пользователя из кэша по ключу."""
        pass
