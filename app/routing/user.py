import logging
from typing import List

from fastapi import APIRouter, Depends
from rbacx.adapters.fastapi import require_access

from app.models.models import UserCreate, UserPass, UserReturn, UserTokenResponse, UserUpdate
from app.services.dependencies import GetTokenDep, TokenServiceDep, UserRepoDep, UserServiceDep
from auth.guard import guard
from auth.security import make_env_builder

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(__name__)


@router.post("/create", response_model=UserTokenResponse)
async def create_user(user: UserCreate, user_service: UserServiceDep):
    """
    Создание нового пользователя role user и добавление refresh токена в бд
    """
    return await user_service.create_user_with_tokens_service(user=user, role="user")


@router.post("/fast_create_admin", response_model=UserTokenResponse)
async def fast_create_admin(user: UserCreate, user_service: UserServiceDep) -> UserTokenResponse:
    # нужно что-то делать если все сломалось после commit но до return(midlwear, bg_task)
    return await user_service.create_user_with_tokens_service(user=user, role="admin")


@router.get(
    "/get_all",
    dependencies=[Depends(require_access(guard, make_env_builder("view_user", "page")))],
    response_model=List[UserReturn],
)
async def get_all_users(
    user_repo: UserRepoDep,
    skip: int = 0,
    limit: int = 10,
):
    return await user_repo.get_all_base_repo(skip=skip, limit=limit)


@router.post("/refresh")
async def get_access_token(refresh_token: GetTokenDep, token_service: TokenServiceDep) -> dict:
    "проверка входного refresh токена и генерация access"

    access_token = await token_service.make_token_access_via_refresh_service(refresh_token)
    return {"access_token": access_token}


@router.post("/log_in", response_model=UserTokenResponse)
async def log_in(user: UserPass, user_service: UserServiceDep):
    """Log In юзера с проверкой пароля и токена.
    если токен is_active = False юзер ен войдет (нужно будет менять пароль и т.п.)
    реализовывать смену не планирую и такие юзеры пока будут бесполезны
    """

    return await user_service.login_user_service(username=user.username, password=user.password)


@router.get("/me", response_model=UserReturn)
async def get_current_user_info(user_service: UserServiceDep, token: GetTokenDep):
    """
    Получить информацию о текущем пользователе из access токена.
    """
    return await user_service.get_current_user_from_token_serv(token)


@router.get("/{user_id}", response_model=UserReturn)
async def get_user_by_id(user_id: int, user_service: UserServiceDep):
    """get user by id"""
    return await user_service.get_user_serv(user_id)


@router.post(
    "{user_id}",
    dependencies=[Depends(require_access(guard, make_env_builder("admin_only", "page")))],
    response_model=UserReturn,
)
async def update_username(user_id: int, new_info: UserUpdate, user_service: UserServiceDep):
    """обновление только username доступно админу"""
    return await user_service.update_userinfo_serv(user_id, new_info)


@router.delete("/user_id")
async def delete_user_by_id(user_id: int, user_service: UserServiceDep) -> dict:
    """удаления пользователя по id со всеми задачами на нем
    для простоты отладки без доступа по RBAC
    """
    return await user_service.delete_user_by_id_service(user_id)
