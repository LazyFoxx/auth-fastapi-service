from dataclasses import asdict
from datetime import datetime
from typing import Optional

import redis.asyncio as aioredis

from src.application.interfaces.user_cache_repository import (
    UserCacheRepository,
)  # Зависит от интерфейса Application слоя
from src.domain.entities.user import (
    User as DomainUser,
)  # Зависит от доменной модели


# Выбираем подход: хранение как JSON String
class UserRedisRepositoryImpl(UserCacheRepository):
    """Реализация UserCacheRepository с использованием Redis Hash.
    Это адаптер для Redis.
    """

    def __init__(self, redis_client: aioredis.Redis):
        # Репозиторий зависит от абстракции клиента Redis (даже если aioredis.Redis - это конкретный класс,
        # мы передаем его как зависимость, а не создаем внутри)
        self._redis_client = redis_client

    async def get(self, key: str) -> Optional[DomainUser]:
        """Получить пользователя из кэша по ключу."""
        user_dict = await self._redis_client.hgetall(key)

        if user_dict:
            return DomainUser(
                email=user_dict["email"],
                username=user_dict["username"],
                password_hash=user_dict["password_hash"],
                verification_code=user_dict["verification_code"],
            )

        return None

    async def save(self, key: str, user: DomainUser, ttl: int) -> Optional[DomainUser]:
        """Сохранить пользователя в кэше по ключу с указанным временем жизни (TTL)."""
        try:
            user_dict = asdict(user)

            # Преобразование неподдерживаемых типов (например, datetime)
            for k, value in user_dict.items():
                if isinstance(value, datetime):
                    user_dict[key] = value.isoformat()
                if value is None:
                    user_dict[k] = "None"

            await self._redis_client.hset(key, mapping=user_dict)
            await self._redis_client.expire(key, ttl)

            user = await self.get(key)
            print(user)
            print("ключ", key)

            return user
        except Exception as ex:
            print(f"redis {ex}")
            return None

    async def delete(self, key: str) -> Optional[True]:
        """Удалить пользователя из кэша по ключу."""
        result = await self._redis_client.delete(key)

        if result:
            return True
        return None
