import logging
from datetime import datetime, timezone
from typing import List

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User
from starlette import status

from DataBase.Database import get_async_session
from DataBase.Shemas import UserDB
from app.exceptions import CustomException
from app.logger import logger
from app.models.models import UserReturn, UserCreate, UserBase, UserTokenResponse
from app.services.hash_password import PasswordService
from auth.security import create_access_token, create_refresh_token

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/create", response_model=UserTokenResponse)
async def create_user(
        user: UserCreate,
        session: AsyncSession = Depends(get_async_session)
):
    logger.info(f"Creating user: {user.username}")
    """
    Создание нового пользователя в базе данных.

    Возвращает:
    - UserReturn с данными созданного пользователя и ID из БД

    Пример тела запроса:
    {
        "username": "string",
        "info": "string",
        "password": "string"
    }
    """

    # возможна гонка но глобальный Exceptiom hendler даст 500 из-за
    # username = Column(String(45), nullable=False, unique=True
    stmt = select(UserDB).where(UserDB.username == user.username)
    user_lrdy_exist = await session.scalar(stmt)
    if user_lrdy_exist:
        raise CustomException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Costum exception user lrdy exist',
            message='some message caz i can'
        )

    try:
        # Создаем объект БД
        user_dict = user.model_dump()
        db_user = UserDB(**user_dict)

        # Добавляем и сохраняем
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)  # запрашиваем  ID из DB т.к. при commit id еще не сушществует

        access_token = create_access_token({user.username: user.username})
        refresh_token = create_refresh_token({user.username: user.username})

        return UserTokenResponse(
            id=db_user.id,
            username=db_user.username,
            info=db_user.info,
            access_token=access_token,
            refresh_token=refresh_token
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'ошибка создания пользователя {str(e)}'
        )


@router.get("/get_all", response_model=List[UserReturn])
async def get_all_users(
        skip: int = 0,
        limit: int = 10,
        session: AsyncSession = Depends(get_async_session)
):
    """
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
