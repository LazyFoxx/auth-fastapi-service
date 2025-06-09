# Импортируем все ORM модели здесь, чтобы Base.metadata их увидел
from src.infrastructure.database.models.user_model import User

# Можно также импортировать Base из database.py, если она нужна здесь


__all__ = ["User", "Ingredient"]
