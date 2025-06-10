import logging

import redis.asyncio as aioredis

from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class RedisClientManager:

    def __init__(self) -> None:
        self.__client = None
        self.__redis_url = settings.REDIS_URL

    async def connect(self) -> aioredis.Redis:
        """Создает и подключает клиент Redis."""
        try:
            client = aioredis.from_url(
                self.__redis_url, decode_responses=True, max_connections=10
            )
            await client.ping()
            logger.info("Successfully connected to Redis.")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Корректно закрывает клиент Redis."""
        if self.__client:
            await self.__client.close()
            self.__client = None
            logger.info("Redis connection closed.")

    async def get_client(self) -> aioredis.Redis:
        """Возвращает клиент Redis из состояния приложения."""
        if self.__client is None:
            self.__client = await self.connect()
        return self.__client


RedisClient = RedisClientManager()
