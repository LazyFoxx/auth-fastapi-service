from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession  # Используем асинхронную сессию

from src.application.interfaces.user_repository import (
    UserRepository,
)  # Зависит от интерфейса Application слоя
from src.domain.entities.user import (
    User as DomainUser,
)  # Зависит от доменной модели
from src.infrastructure.database.models.user_model import (
    User as DBUser,
)  # Зависит от ORM модели Infrastructure слоя


class UserRepositoryImpl(UserRepository):
    """Реализация репозитория пользователей с использованием async SQLAlchemy."""

    def __init__(self, db_session: AsyncSession):
        """Инициализация асинхронного репозитория.

        Args:
            db_session (AsyncSession): сессия полученная через фабрику сессий.

        """
        self.db_session = db_session

    # Вспомогательные методы для преобразования между Domain и ORM моделями
    # Эти преобразования происходят на границе Infrastructure и Application/Domain
    async def _to_domain(self, db_user: DBUser) -> DomainUser:
        return DomainUser(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            password_hash=db_user.password_hash,
        )

    async def _to_db(self, domain_user: DomainUser) -> DBUser:
        # Если у доменной модели есть ID, пытаемся найти
        # существующую ORM модель для обновления
        if domain_user.id is not None:
            # В асинхронном коде используем execute с select
            result = await self.db_session.execute(
                select(DBUser).filter(DBUser.id == domain_user.id)
            )
            db_user = result.scalar_one_or_none()
            if db_user:
                # Обновляем поля существующей ORM модели
                db_user.username = domain_user.username
                db_user.email = domain_user.email
                db_user.password_hash = domain_user.password_hash

                return db_user

        # Если ID нет или объект не найден, создаем новую ORM модель
        return DBUser(
            username=domain_user.username,
            email=domain_user.email,
            password_hash=domain_user.password_hash,
        )

    async def save(self, user: DomainUser) -> DomainUser:
        """Сохраняет пользоватея в БД.

        Args:
            user (DomainUser): Обьект пользователя.

        Returns:
            DomainUser: Возвращает обьект пользователя.

        """
        db_user = await self._to_db(user)
        self.db_session.add(db_user)
        await self.db_session.commit()
        await self.db_session.refresh(
            db_user
        )  # Обновляем объект для получения ID, если был None
        return await self._to_domain(db_user)

    async def get_user(
        self, username: Optional[str] = None, email: Optional[str] = None
    ) -> Optional[DomainUser]:
        """Возвращает пользователя по username или email если он существует.

        Args:
            username (str): Username пользователя.
            email (str): Email адрес пользователя для поиска.

        Returns:
            Optional[DomainUser]: Объект пользователя, если найден, иначе None.

        Raises:
            ValueError: Если не передан ни username, ни email.

        """

        if not username and not email:
            raise ValueError(
                "Необходимо указать хотя бы один параметр: username или email"
            )

        filters = []
        if username:
            filters.append(DBUser.username == username)
        if email:
            filters.append(DBUser.email == email)

        result = await self.db_session.execute(select(DBUser).filter(or_(*filters)))

        db_user = result.scalar_one_or_none()
        if db_user is None:
            return None
        return await self._to_domain(db_user)
