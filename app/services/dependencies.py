from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.fin_todoo_service import FinTodooService
from app.services.todoo_service import TodooService
from app.services.token_service import TokenService
from app.services.user_service import UserService
from auth.security import oauth2_scheme
from DataBase.Database import get_async_session
from DataBase.repository.finished_todoo_repo import FinishedTodooRepository
from DataBase.repository.todoo_repository import TodooRepository
from DataBase.repository.token_repository import TokenRepository
from DataBase.repository.user_repository import UserRepository


# репозитории--------------------------------------------
async def get_user_repo(
    db: AsyncSession = Depends(get_async_session),
) -> UserRepository:  # <- Сессия #1
    return UserRepository(db)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]


async def get_token_repo(
    session: AsyncSession = Depends(get_async_session),  # <- точно та же Сессия #1 (проверено по id)
) -> TokenRepository:
    return TokenRepository(session)


TokenRepoDep = Annotated[TokenRepository, Depends(get_token_repo)]


async def get_todoo_repo(
    session: AsyncSession = Depends(get_async_session),  # <- точно та же Сессия #1 (проверено по id)
) -> TodooRepository:
    return TodooRepository(session)


TodooRepoDep = Annotated[TodooRepository, Depends(get_todoo_repo)]


async def get_finished_todoo_repo(
    session: AsyncSession = Depends(get_async_session),  # <- точно та же Сессия #1 (проверено по id)
) -> FinishedTodooRepository:
    return FinishedTodooRepository(session)


FinTodooRepoDep = Annotated[FinishedTodooRepository, Depends(get_finished_todoo_repo)]


# сервисы--------------------------------------------
async def get_token_service(token_repo: TokenRepoDep) -> TokenService:
    return TokenService(token_repo=token_repo)


TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


async def get_todoo_service(
    todoo_repo: TodooRepoDep, user_repo: UserRepoDep, f_todoo_repo: FinTodooRepoDep
) -> TodooService:
    return TodooService(todoo_repo=todoo_repo, user_repo=user_repo, f_todoo_repo=f_todoo_repo)


TodooServiceDep = Annotated[TodooService, Depends(get_todoo_service)]


async def get_fin_todoo_service(todoo_repo: TodooRepoDep, f_todoo_repo: FinTodooRepoDep) -> FinTodooService:
    return FinTodooService(todoo_repo=todoo_repo, f_todoo_repo=f_todoo_repo)


FinTodooServiceDep = Annotated[FinTodooService, Depends(get_fin_todoo_service)]


async def get_user_service(
    user_repo: UserRepoDep,  # <- UserRepository с Сессией #1
    token_service: TokenServiceDep,  # <- TokenService с TokenRepository (та же Сессия #1)
) -> UserService:
    """Создаёт ЭКЗЕМПЛЯР UserService с обеими зависимостями"""
    return UserService(user_repo=user_repo, token_service=token_service)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


# dependencies с другим контекстом использования----------
async def get_token_from_request(token: str = Depends(oauth2_scheme)) -> str:
    """Извлекает refresh токен из запроса"""
    return token


# тип-аннотация (вроде бы удобнее с ними)
GetTokenDep = Annotated[str, Depends(get_token_from_request)]
