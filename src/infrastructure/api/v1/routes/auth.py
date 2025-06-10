from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status

# Импорты из Application (Сервис, Порт, Ошибки)
from src.application.use_cases.user_service import (
    DuplicateUserEmailError,
    DuplicateUserUsernameError,
)
from src.config import settings
from src.domain.entities.user import User as DomainUser

# Импорты из Infrastructure (Pydantic схемы, зависимости БД)
from src.infrastructure.api.v1.schemas.users import (
    UserCreate,
)
from src.infrastructure.api.v1.schemas.verify_code import VerifyCode
from src.infrastructure.dependencies import (
    UserServiceDep,
)

router = APIRouter(
    prefix="/v1/auth",
    tags=["auth"],
)


@router.post("/register/")
async def register(
    user: UserCreate,
    response: Response,
    service: UserServiceDep,
):
    """Первый этап регистрации.
    Принимает username password emai и отправляет код подтверждения на email.
    Возвращает временный токен для идентификации в headers.
    """
    try:

        domain_user = DomainUser(
            username=user.username, password_hash=user.password, email=user.email
        )

        token = await service.register(domain_user)
        response.headers["authorization"] = f"Bearer {token}"
        return

    except DuplicateUserEmailError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DuplicateUserUsernameError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        # Обработка других потенциальных ошибок
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/register/verify/")
async def register_verify_code(
    code: VerifyCode,
    response: Response,
    service: UserServiceDep,
    authorization: Annotated[str, Header()],
):
    """Второй этап регистрации.
    Принимает код верификации и временнй токен (если он не истек)
    и возвращает jwt токен доступа и рефреш токен если код совпадает
    """
    try:

        token = authorization.replace("Bearer ", "")

        access_token, refresh_token = await service.verify_code(code.code, token=token)
        response.headers["authorization"] = f"Bearer {access_token}"

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Для локальной разработки
            samesite="lax",  # Для локальной разработки
            max_age=settings.token.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

    except Exception as e:
        # Обработка других потенциальных ошибок
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# @router.post("/login/")
# @router.post("/logout/")
# @router.post("/reset-password/")
# @router.post("/verify-recovery/")
