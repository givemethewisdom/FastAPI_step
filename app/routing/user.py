from typing import List

from fastapi import Depends, HTTPException, APIRouter
from rbacx.adapters.fastapi import require_access
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User
from starlette import status

from DataBase.Database import get_async_session
from DataBase.Shemas import UserDB
from app.models.models import UserReturn, UserCreate, UserBase, UserTokenResponse
from auth.dependencies import get_current_user
from auth.guard import guard
from auth.security import get_user_from_token, make_env_builder

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/admin", dependencies=[
    Depends(require_access(guard, make_env_builder("view_user", "page")))
])
async def admin_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/create", response_model=UserTokenResponse)
async def create_user(
        user: UserCreate,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Создание нового пользователя.
    """
    try:
        from DataBase.repository import create_user_with_tokens
        return await create_user_with_tokens(user, session)

    except HTTPException:
        # Пробрасываем HTTP исключения как есть
        raise

    except Exception as e:
        # Обработка неожиданных ошибок
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания пользователя: {str(e)}"
        )


@router.get("/get_all", dependencies=[
    Depends(require_access(guard, make_env_builder("view_user", "page")))
], response_model=List[UserReturn])
async def get_all_users(
        skip: int = 0,
        limit: int = 10,
        session: AsyncSession = Depends(get_async_session),

):
    """
    делаем 2 разных запроса т.к. RBAC использует синхронное подключение и хранить роль в токене не хочется
    Получение информации о всех порльзователях.

    Параметры:
    - skip - смещение
    - limit - Кол-во юзеров

    Возвращает:
    - Данные пользователей в формате UserReturn
    - пуцстой список если нет пользователей
    """
    try:
        query = await session.execute(
            select(UserDB)
            .offset(skip)
            .limit(limit)
            .order_by(UserDB.id)
        )

        users = query.scalars().all()

        return users

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'ошибка получения информации о пользователях {str(e)}'
        )


@router.get("/me")
async def get_current_user_info(
        username: str = Depends(get_user_from_token)
):
    """
    Получить информацию о текущем пользователе.
    Требует access токен в заголовке Authorization.
    """
    # username уже извлечен из токена
    return {
        "message": {username}
    }
# 4) Маршрут для админов — проверяем доступ через rbacx


@router.get("/{user_id}", response_model=UserReturn)
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Получение информации о пользователе по его ID.

    Параметры:
    - user_id: идентификатор пользователя в БД

    Возвращает:
    - Данные пользователя в формате UserReturn
    - 404 ошибку если пользователь не найден
    """
    try:
        user = await session.get(UserDB, user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")

        return user

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'ошибка получения информации о пользователе {str(e)}'
        )


# Роут для полного обновления информации о пользователе по ID
@router.put('/{user_id}', response_model=UserReturn)
async def update_user(
        user_id: int,
        user: UserBase,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Полное обновление данных пользователя по ID.

    Параметры:
    - user_id: ID пользователя в базе данных
    - user: новые данные пользователя (все кроме info обязательно)

    Возвращает:
    - Обновленные данные пользователя в формате UserReturn
    - 404 ошибку если пользователь не найден
    - 500 ошибку при проблемах с базой данных

    Пример запроса:
    {
        "username": "string",
        "info": "string",
    }
    """
    try:
        update_data = user.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="have no new data")
        query = (
            update(UserDB)
            .where(UserDB.id == user_id)
            .values(**update_data)
            .returning(UserDB)
        )

        result = await session.execute(query)
        new_user_data = result.scalar_one_or_none()

        if not new_user_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="user not found")

        await session.commit()
        return new_user_data

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'ошибка добавления данных о пользователе {str(e)}'
        )


# Роут для удаления пользователя по ID
@router.delete("/{user_id}", response_model=dict)
async def delete_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Удаление пользователя каскадно из базы данных по ID.

    Параметры:
    - user_id: идентификатор пользователя для удаления

    Возвращает:
    - Сообщение об успешном удалении
    - 404 ошибку если пользователь не найден
    - 500 ошибку при проблемах с базой данных
    """
    try:
        stmt = (delete(UserDB)
                .where(UserDB.id == user_id))

        result = await session.execute(stmt)

        if not result.rowcount:
            raise HTTPException(
                status_code=404,
                detail="Пользователь с указанным ID не найден"
            )
        await session.commit()
        return {'user deleted with id': user_id}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка удаления пользователя: {str(e)}"
        )
