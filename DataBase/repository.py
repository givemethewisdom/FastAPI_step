from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.testing.pickleable import User

from DataBase.Shemas import UserDB, TokenDB
from app.models.models import UserCreate
from app.services.hash_password import pwd_context

"""тут много лишнего нужно разделять (как-нибудь в другой раз)"""


async def get_user(username: str, db: AsyncSession) -> User | None:
    """
    Получение пользователя из БД, где roles хранится как строка.
    Например: "admin" или "user,admin" или "user"
    """
    from sqlalchemy import select

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
    roles_str = db_user.roles

    # Разделяем строку по запятой и убираем пробелы
    if "," in roles_str:
        roles_list = [role.strip() for role in roles_str.split(",")]
    else:
        roles_list = [roles_str.strip()] if roles_str.strip() else ["user"]

    # Конвертируем SQLAlchemy модель в Pydantic модель
    return User(
        username=db_user.username,
        roles=roles_list,  # Теперь это список
        info=db_user.info,  # или другое поле, если есть
    )


async def check_user_exists(username: str, db: AsyncSession) -> bool:
    """Проверить существует ли пользователь"""
    result = await db.execute(
        select(UserDB).where(UserDB.username == username)
    )
    return result.scalar_one_or_none() is not None


async def create_new_user(user_data: UserCreate, db: AsyncSession) -> UserDB:
    """
    Создать нового пользователя в БД.
    Возвращает SQLAlchemy модель UserDB.
    """

    hashed_password = pwd_context.hash(user_data.password)

    # Создаем пользователя
    db_user = UserDB(
        username=user_data.username,
        password=hashed_password,  # Храним хеш!
        info=user_data.info,
        roles='user'  # Все новые пользователи получают роль 'user'
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# async def delete_refresh_token(user_id:int, db:AsyncSession)->bool:
# 'Удаляет токен по юзер ID'
# await db.execute(
# delete(TokenDB).where(TokenDB.user_id == user_id)
# )
# return True
async def save_refresh_token(user_id: int, token_hash: str, expire_at, db: AsyncSession):
    await db.execute(
        delete(TokenDB).where(TokenDB.user_id == user_id)
    )

    db_token = TokenDB(
        user_id=user_id,
        refresh_token=token_hash,
        expires_at=expire_at,
    )

    db.add(db_token)
    await db.commit()
    return db_token
