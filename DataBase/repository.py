from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.testing.pickleable import User

from DataBase.Shemas import UserDB

USERS_DATA = [
    {
        "username": "admin",
        "password": "adminpass",  # В продакшене пароли должны быть хешированы!
        "roles": ["admin"],
        "full_name": "Admin User",
        "email": "admin@example.com",
        "disabled": False
    },
    {
        "username": "user",
        "password": "userpass",
        "roles": ["user"],
        "full_name": "Regular User",
        "email": "user@example.com",
        "disabled": False
    },
]


async def get_user(username: str, db: AsyncSession) -> User | None:
    """
    Получение пользователя из БД, где roles хранится как строка.
    Например: "admin" или "user,admin" или "user"
    """
    from sqlalchemy import select

    # Простой запрос без selectinload
    result = await db.execute(
        select(UserDB).where(UserDB.username == username)
    )
    db_user = result.scalar_one_or_none()

    if not db_user:
        return None

    # Преобразуем строку roles в список
    # Если roles это "admin" -> ["admin"]
    # Если roles это "user,admin" -> ["user", "admin"]
    # Если roles это None или пустая строка -> ["user"] (по умолчанию)
    roles_str = db_user.roles or "user"

    # Разделяем строку по запятой и убираем пробелы
    if "," in roles_str:
        roles_list = [role.strip() for role in roles_str.split(",")]
    else:
        roles_list = [roles_str.strip()] if roles_str.strip() else ["user"]

    # Конвертируем SQLAlchemy модель в Pydantic модель
    return User(
        username=db_user.username,
        roles=roles_list,  # Теперь это список
        full_name=db_user.info,  # или другое поле, если есть
        email=None,  # или добавьте поле email в модель
        disabled=False  # или добавьте поле disabled
    )
