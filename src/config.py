import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from pydantic import EmailStr, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTConfig(BaseSettings):
    """Настройки JWT"""

    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    PUBLIC_KEY: str
    PRIVATE_KEY: str

    @validator("PRIVATE_KEY")
    @classmethod
    def validate_private_key(cls, value: str, values: dict):
        try:
            return serialization.load_pem_private_key(
                value.replace("\\n", "\n").encode("utf-8"),
                password=None,
                backend=default_backend(),
            )
        except Exception as e:
            raise ValueError(f"Invalid private key: {str(e)}")


class SMTPConfig(BaseSettings):
    """Настройки SMTP сервера"""

    server: str = Field(min_length=1)
    port: int = Field(ge=1, le=65535)
    user: EmailStr = Field(min_length=1)
    password: str = Field(min_length=1)


class PostgresConfig(BaseSettings):
    """Настройки Postgress подключения"""

    user: str
    password: str
    host: str
    port: int
    name: str


class Settings(BaseSettings):
    """Настройки."""

    token: JWTConfig = Field(default_factory=JWTConfig)
    psg: PostgresConfig = Field(default_factory=PostgresConfig)
    smtp: SMTPConfig = Field(default_factory=SMTPConfig)
    REDIS_URL: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    def get_db_url(self):
        """Формирует и возвращает ссылку для подключения к БД."""
        return (
            f"postgresql+asyncpg://{self.psg.user}:{self.psg.password}@"
            f"{self.psg.host}:{self.psg.port}/{self.psg.name}"
        )


settings = Settings()
