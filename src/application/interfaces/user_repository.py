from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.user import (
    User as DomainUser,
)  # Зависит от доменной модели!


class UserRepository(ABC):
    """Интерфейс репозитория для работы с пользователями."""

    @abstractmethod
    async def save(self, ingredient: DomainUser) -> DomainUser:
        """Сохраняет или обновляет пользователя. Возвращает сохраненный объект с ID."""
        pass

    @abstractmethod
    async def get_user(
        self, username: Optional[str] = None, email: Optional[str] = None
    ) -> Optional[DomainUser]:
        """Возвращает пользователя по email или username или None, если не найден."""
        pass
