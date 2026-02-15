from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.Database import get_async_session
from DataBase.repository.token_repository import TokenRepository
from DataBase.repository.user_repository import UserRepository
from app.services.token_service import TokenService
from app.services.user_service import UserService
from auth.security import oauth2_scheme


async def get_user_repo(
        db: AsyncSession = Depends(get_async_session)# <- Сессия #1
) -> UserRepository:
    return UserRepository(db)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]


async def get_token_repo(
        session: AsyncSession = Depends(get_async_session)# <- точно та же Сессия #1 (проверено по id)
) -> TokenRepository:
    return TokenRepository(session)


TokenRepoDep = Annotated[TokenRepository, Depends(get_token_repo)]


async def get_token_service(
        token_repo: TokenRepoDep
) -> TokenService:
    return TokenService(token_repo=token_repo)


TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


async def get_user_service(
    user_repo: UserRepoDep,# <- UserRepository с Сессией #1
    token_service: TokenServiceDep# <- TokenService с TokenRepository (та же Сессия #1)
) -> UserService:
    """Создаёт ЭКЗЕМПЛЯР UserService с обеими зависимостями"""
    return UserService(
        user_repo=user_repo,
        token_service=token_service
    )

UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_token_from_request(
    token: str = Depends(oauth2_scheme)
) -> str:
    """Извлекает refresh токен из запроса"""
    return token

# тип-аннотация (вроде бы удобнее с ними)
GetTokenDep = Annotated[str, Depends(get_token_from_request)]