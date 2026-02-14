import logging
from typing import List, Any

from fastapi import Depends, HTTPException, APIRouter
from rbacx.adapters.fastapi import require_access
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User
from starlette import status

from DataBase.Database import get_async_session
from DataBase.Shemas import UserDB

from app.models.models import UserPass, UserTokenResponse, UserCreate, UserReturn, UserBase
from app.services.dependencies import UserRepoDep, UserServiceDep
from app.services.token_service import TokenService
from app.services.user_service import UserService
from auth.dependencies import get_current_user, get_access_from_refresh_token, get_user_from_token
from auth.guard import guard
from auth.security import make_env_builder

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

logger = logging.getLogger(__name__)


@router.post("/create", response_model=UserTokenResponse)
async def create_user(
        user: UserCreate,
        user_service: UserServiceDep
):
    """
    Создание нового пользователя role user и добавление refresh токена в бд
    """
    try:
        return await user_service.create_user_with_tokens_service(
            user=user,
            role='user'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка создания пользователя"
        )
