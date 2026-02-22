import logging

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.testing.pickleable import User
from starlette import status

from app.exceptions import CustomException
from app.models.models import UserCreate
from app.services.hash_password import PasswordService
from DataBase.Shemas import TokenDB, UserDB


# from app.logger import logger


"""тут много лишнего нужно разделять (как-нибудь в другой раз)
upd взе резделено и тут только legacy"""

logger = logging.getLogger(__name__)


async def get_user(username: str, db: AsyncSession) -> User | None:
    """
    Получение пользователя из БД, где roles хранится как строка.
    Например: "admin" или "user,admin" или "user"
    но роль пока у всех только одна. пока пусть будет
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
