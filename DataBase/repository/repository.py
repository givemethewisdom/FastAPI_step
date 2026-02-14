import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy.testing.pickleable import User
from starlette import status

from DataBase.Shemas import UserDB, TokenDB
from app.exceptions import CustomException
# from app.logger import logger

from app.models.models import UserCreate
from app.services.hash_password import PasswordService

"""тут много лишнего нужно разделять (как-нибудь в другой раз)"""

logger = logging.getLogger(__name__)


async def get_user(username: str, db: AsyncSession) -> User | None:
    """
    Получение пользователя из БД, где roles хранится как строка.
    Например: "admin" или "user,admin" или "user"
    """

    db_user = await check_user_exists(username=username, db=db)
    logger.debug(db_user)

    if not db_user:
        return None

    # Преобразуем строку roles в список
    # Если roles это "admin" -> ["admin"]
    # Если roles это "user,admin" -> ["user", "admin"]
    # Если roles это None или пустая строка -> ["guest"] (по умолчанию)
    roles_str = db_user.roles

    # Разделяем строку по запятой и убираем пробелы
    if "," in roles_str:
        roles_list = [role.strip() for role in roles_str.split(",")]
    else:
        roles_list = [roles_str.strip()] if roles_str.strip() else ["guest"]

    return User(
        username=db_user.username,
        roles=roles_list,  # Теперь это список
        info=db_user.info,
    )





async def delete_refresh_token(user_id: int, db: AsyncSession) -> bool:
    """Удаляет токен по юзер ID"""
    # просто накидал. надо доделать
    await db.execute(
        delete(TokenDB).where(TokenDB.user_id == user_id)
    )
    return True




async def get_refresh_token(user_id: int, db: AsyncSession) -> TokenDB | None:
    try:
        res = await db.execute(
            select(TokenDB).where(TokenDB.user_id == user_id)
        )

        refresh_token = res.scalar_one_or_none()

        if not refresh_token:
            return None

        return refresh_token

    except Exception as e:
        # вообще таукие ошибки глобал хендлер будет перехватывать
        logger.error('Some server problem: %s', e)
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='server error',
            message='Я уже не знаю что тут придумать'
        )
