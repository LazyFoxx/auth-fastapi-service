from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Базовая схема (модель) для представления пользователя."""

    username: str = Field(..., description="Логин пользователя")


class UserCreate(UserBase):
    """Схема (модель) для создания и добавления пользователя."""

    email: EmailStr = Field(..., description="email пользователя")
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="Пароль пользователя",
    )

    @field_validator("password")
    @classmethod  # В Pydantic v2 валидаторы полей должны быть classmethod
    def validate_password_complexity(cls, value: str) -> str:
        """Проверяет сложность пароля."""
        if not any(c.isupper() for c in value):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not any(c.islower() for c in value):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not any(c.isdigit() for c in value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")

        return value

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "ngdis13",
                "email": "ngdis13@mail.ru",
                "password": "34kmffwFDe344",
            }
        }
    }
