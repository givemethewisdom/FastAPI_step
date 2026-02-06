from typing import List

from fastapi import Depends, HTTPException, APIRouter
from rbacx.adapters.fastapi import require_access
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User
from starlette import status

from DataBase.Database import get_async_session
from DataBase.Shemas import UserDB
from app.logger import logger
from app.models.models import UserReturn, UserCreate, UserBase, UserAccessResponse
from app.models.models_token import RefreshTokenResponse
from app.services.token_service import TokenService
from app.services.user_service import UserService
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


@router.post('/login')
async def login(
        username: str,
        password: str,
        session: AsyncSession = Depends(get_async_session)
):

    "get refresh token by user name"
    try:
        if not login_user():


        token_service = TokenService()
        res = await token_service.get_refresh_token_from_db(user_id=, db_session=session)
        return res

    except HTTPException:
        raise

    except Exception as e:
        "есть глобал хендлер и это по сути не нужно"
        logger.error(f'some error in @router.get("/get_user_token"): {e}')  # все еще не уверен на счет f-string
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='unexpected server error'
        )

@router.post("/fast_create_admin", response_model=UserReturn)
async def fast_create_admin(
        user: UserCreate,
        session: AsyncSession = Depends(get_async_session)
) -> UserAccessResponse:

    user_service = UserService()
    new_user_info = await user_service.create_user_with_tokens(
        user=user,
        role='admin',
        db=session,
    )

    return new_user_info


# get token решил сделать по username хотя лучше было бы по id (наверное)
@router.get("/get_user_token")
async def get_user_token(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    "просто быстрый способ получить токен для отладки"
    try:
        token_service = TokenService()
        res = await token_service.get_refresh_token_from_db(user_id=user_id, db_session=session)
        return res

    except HTTPException:
        raise

    except Exception as e:
        "есть глобал хендлер и это по сути не нужно"
        logger.error(f'some error in @router.get("/get_user_token"): {e}')  # все еще не уверен на счет f-string
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='unexpected server error'
        )


@router.post("/create", response_model=UserAccessResponse)
async def create_user(
        user: UserCreate,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Создание нового пользователя.и добавление хеша его access токена в бд
    """
    try:
        user_service = UserService()
        new_user_info = await user_service.create_user_with_tokens(
            user=user,
            role='user',
            db=session
        )

        token_service = TokenService()
        await token_service.save_refresh_token_in_db(
            user_id=new_user_info.id,
            token=new_user_info.refresh_token,
            db_session=session
        )
        return new_user_info

    except HTTPException:
        # Пробрасываем HTTP исключения как есть
        raise

    except Exception as e:
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
    """
    return {
        "message": {username}
    }


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
