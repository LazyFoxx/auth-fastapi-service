from datetime import datetime
from typing import Annotated

from sqlalchemy import Integer, func
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from src.config import settings

DATABASE_URL = settings.get_db_url()

# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(url=DATABASE_URL)
# Создаем фабрику сессий для взаимодействия с базой данных
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

uniq_str_an = Annotated[str, mapped_column(unique=True)]


# Базовый класс для всех моделей
class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей.

    Args:
        AsyncAttrs (class): Основной класс для всех моделей,
        от которого будут наследоваться все таблицы (модели таблиц).
        DeclarativeBase (class): Позволяет создавать асинхронные модели.

    """

    __abstract__ = (
        True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower() + "s"
