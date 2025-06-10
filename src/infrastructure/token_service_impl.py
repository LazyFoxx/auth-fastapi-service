import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt

from src.application.interfaces.token_service import TokenService


class TokenServiceImpl(TokenService):
    """Интерфейс (порт) для работы с токенами."""

    def __init__(self, settings) -> None:
        self.__ALGORITHM = settings.ALGORITHM
        self.__ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.__REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
        self.__PUBLIC_KEY = settings.PUBLIC_KEY
        self.__PRIVATE_KEY = settings.PRIVATE_KEY

    async def generate_token(self, email: str) -> str:
        """генерирует уникальный токен по email."""
        return hashlib.sha256(email.encode()).hexdigest()

    async def create_access_token(self, data: dict) -> str:
        """генерирует jwt access token."""
        if "sub" not in data:
            raise ValueError("Payload должен содержать поле 'sub'")
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.__ACCESS_TOKEN_EXPIRE_MINUTES
        )
        jti = str(uuid.uuid4())
        to_encode.update({"exp": expire, "type": "access", "jti": jti})
        access_token = jwt.encode(
            to_encode, self.__PRIVATE_KEY, algorithm=self.__ALGORITHM
        )
        return access_token

    async def create_refresh_token(self, data: dict) -> str:
        if "sub" not in data:
            raise ValueError("Payload must contain 'sub' field")
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=self.__REFRESH_TOKEN_EXPIRE_DAYS
        )
        jti = str(uuid.uuid4())
        to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
        refresh_token = jwt.encode(
            to_encode, self.__PRIVATE_KEY, algorithm=self.__ALGORITHM
        )
        return refresh_token

    async def verify_token(self, token: str) -> dict:
        """Декодирует jwt и возвращает payload."""
