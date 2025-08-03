import random

from src.application.interfaces.email_service import EmailService
from src.application.interfaces.password_hasher_repository import PasswordHasher
from src.application.interfaces.token_service import TokenService
from src.application.interfaces.user_cache_repository import UserCacheRepository
from src.application.interfaces.user_repository import (
    UserRepository,
)  # Зависит от интерфейса!
from src.config import settings
from src.domain.entities.user import User as DomainUser


# Определяем кастомные ошибки для Application слоя
class DuplicateUserEmailError(Exception):
    """Пользователь с таким email уже существует."""

    pass


class DuplicateUserUsernameError(Exception):
    """Пользователь с таким username уже существует."""

    pass


class UserService:
    """Сервис для управления пользователями."""

    def __init__(
        self,
        email_service: EmailService,
        user_cache: UserCacheRepository,
        repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ):
        """Инициализирует сервис пользователей с репозиторием и хешером паролей.

        Args:
            repository (UserRepository): реализация репозитория.
            password_hasher (PasswordHasher): реализация хешера.
            cache (UserCacheRepository): реализация редис.
            email_service (EmailService): реализация email service.
            token_service: (TokenService): реализация токен сервиса.
            user_cache: (UserCacheRepository): реализация кэша.


        """
        # Сервис зависит от абстракции (интерфейса), а не от конкретной реализации
        self._repository = repository
        self._password_hasher = password_hasher
        self._cache = user_cache
        self._email_service = email_service
        self._token_service = token_service

    async def _check_user(self, user: DomainUser) -> None:
        """Проверяем уникальность email и username пользователя."""
        existing_user = await self._repository.get_user(user.email)
        if existing_user:
            raise DuplicateUserEmailError(
                f"Пользователь с таким email '{user.email}' уже существует."
            )
        existing_user = await self._repository.get_user(user.username)
        if existing_user:
            raise DuplicateUserUsernameError(
                f"Пользователь с таким username '{user.username}' уже существует."
            )

    async def _get_password_hash(self, user: DomainUser) -> DomainUser:
        """хеширует пароль пользователя."""
        user.password_hash = await self._password_hasher.get_password_hash(
            user.password_hash
        )
        return user

    async def _create_user(self, user: DomainUser) -> DomainUser:
        """Создает нового пользователя."""
        return await self._repository.save(user)

    async def register(self, user: DomainUser) -> str:
        """Регистрация пользователя 1-я ступень.

        Добавление пользователя и кода верефикации
        в кэш и возвращает токен временной сессии.

        """
        try:
            await self._check_user(user)  # Проверяем уникальность пользователя
            code = "".join([str(random.randint(1, 9)) for _ in range(6)])
            user.verification_code = code

            token = await self._token_service.generate_token(user.email)
            await self._email_service.send_verification_email(user.email, code)

            await self._cache.save(token, user, ttl=600)
            print(code)
        except Exception as e:
            print(e)
        return token

    async def register_verify(self, code: str, token: str) -> tuple[str, str] | None:
        """Регистрация пользователя 2-я ступень.

        если код верификации верный то то генерирует токены
        доступа и добавляет пользователя в базу данных.

        """
        try:
            user = await self._cache.get(token)

            if user is None:
                raise ValueError("Токен недействителен")

            if code != user.verification_code:
                raise ValueError("Неверный код!")

            user = await self._create_user(user)
            print(user)
            # await self._cache.delete(token)

            jwt_payload = {"sub": user.id}
            access_token = await self._token_service.create_access_token(
                data=jwt_payload
            )
            refresh_token = await self._token_service.create_refresh_token(
                data=jwt_payload
            )

            await self._cache.save(
                refresh_token,
                user,
                ttl=24 * 60 * 60 * settings.token.REFRESH_TOKEN_EXPIRE_DAYS,
            )

            return access_token, refresh_token

        except Exception as e:
            print(e)
            return None


# В функции проверки токена вы проверяете поле "type":
# def verify_token(token: str, expected_type: str) -> dict:
#     payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     if payload.get("type") != expected_type:
#         raise HTTPException(status_code=401, detail="Неверный тип токена")
#     return payload
# Пример вызова:
# # Для access-токена
# payload = verify_token(access_token, "access")
# # Для refresh-токена
# payload = verify_token(refresh_token, "refresh")
