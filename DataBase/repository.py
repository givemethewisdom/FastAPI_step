from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.testing.pickleable import User
from starlette import status

from DataBase.Shemas import UserDB
from app.models.models import UserCreate, UserTokenResponse
from app.services.hash_password import pwd_context
from auth.security import create_access_token, create_refresh_token
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


async def create_user_with_tokens(user_data: UserCreate, db: AsyncSession) -> UserTokenResponse:
    """
    Полный цикл создания пользователя с токенами.
    """
    if await check_user_exists(user_data.username, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь {user_data.username} уже существует"
        )

    # 2. Создаем пользователя в БД
    db_user = await create_new_user(user_data, db)

    # 3. Создаем токены
    access_token = create_access_token({'sub': db_user.username})
    refresh_token = create_refresh_token({'sub': db_user.username})

    # 4. Формируем ответ
    return UserTokenResponse(
        id=db_user.id,
        username=db_user.username,
        info=db_user.info,
        access_token=access_token,
        refresh_token=refresh_token
    )
