# infrastructure/security/password_hasher_impl.py
import asyncio

from passlib.context import CryptContext

from src.application.interfaces.password_hasher_repository import PasswordHasher


class PasswordHasherImpl(PasswordHasher):
    """Реализация PasswordHasher с использованием passlib для асинхронных приложений."""

    def __init__(self):
        """Настраиваем passlib с Argon2 или bcrypt."""
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=14,  # Настройка для bcrypt
        )

    async def get_password_hash(self, password: str) -> str:
        """Выполняет хеширование пароля и возвращает hash."""
        loop = asyncio.get_event_loop()
        # Выполняем хеширование в ThreadPoolExecutor
        hashed = await loop.run_in_executor(
            None, self.pwd_context.hash, password  # ThreadPoolExecutor по умолчанию
        )
        return hashed

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Сравнивает текущий пароль и hash пароля и возвращает булевое значение."""
        loop = asyncio.get_event_loop()
        # Выполняем проверку в ThreadPoolExecutor
        is_correct = await loop.run_in_executor(
            None,  # ThreadPoolExecutor по умолчанию
            self.pwd_context.verify,
            plain_password,
            hashed_password,
        )
        return is_correct
