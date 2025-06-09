from typing import AsyncGenerator, Annotated
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from src.infrastructure.database.database import async_session_maker
from src.application.interfaces.email_service import EmailService
from src.application.interfaces.user_repository import UserRepository
from src.application.interfaces.user_cache_repository import UserCacheRepository
from src.application.use_cases.user_service import UserService
from src.application.interfaces.token_service import TokenService
from src.application.interfaces.password_hasher_repository import PasswordHasher
from src.infrastructure.email.email_client_manager import SMTPClientManager
from src.infrastructure.email.repositories.user_email_repository_impl import EmailServiceImpl

from src.infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)
from src.infrastructure.redis.repositories.user_redis_repository_impl import (
    UserRedisRepositoryImpl,
)
from src.infrastructure.token_service_impl import TokenServiceImpl
from src.infrastructure.redis.redis_client_manager import RedisClient
from src.infrastructure.secure import PasswordHasherImpl
from src.config import settings

async def get_async_db() -> AsyncGenerator:
    """Зависимость FastAPI для получения асинхронной сессии БД."""
    async with async_session_maker() as session:
        yield session


async def get_redis() -> Redis:
    """Зависимость для получения клиента Redis."""
    return await RedisClient.get_client()

async def get_smtp() -> SMTPClientManager:
    """Зависимость для получения менеджера клиента Email."""
    return SMTPClientManager()

async def get_email_service(
    client_manager: SMTPClientManager = Depends(get_smtp)
    ) -> EmailService:
    """Зависимость для получения EmailService."""
    return EmailServiceImpl(client_manager)


async def get_user_repository(
    session: AsyncSession = Depends(get_async_db),
) -> UserRepository:
    """Зависимость для получения UserRepositoryImpl."""
    return UserRepositoryImpl(db_session=session)


async def get_redis_repository(
    client: Redis = Depends(get_redis),
) -> UserCacheRepository:
    """Зависимость для получения UserRedisRepositoryImpl."""
    return UserRedisRepositoryImpl(redis_client=client)


async def get_password_hasher() -> PasswordHasher:
    """Зависимость для получения PasswordHasherImpl."""
    return PasswordHasherImpl()


def get_token_service() -> TokenService:
    """Зависимость для получения TokenServiceImpl."""
    return TokenServiceImpl(settings.token)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    user_cache: UserCacheRepository = Depends(get_redis_repository),
    email_service: EmailService = Depends(get_email_service),
    pass_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
) -> UserService:
    return UserService(
        email_service=email_service,
        user_cache=user_cache,
        repository=user_repo,
        password_hasher=pass_hasher,
        token_service=token_service,
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
