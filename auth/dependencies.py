from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User
from starlette import status

from DataBase.Database import get_async_session
from DataBase.repository import get_user
from app.logger import logger
from app.services.token_service import TokenService
from auth.security import get_user_from_token, check_refresh_token, create_access_token, decode_token


async def get_current_user(
        current_username: str = Depends(get_user_from_token),
        db: AsyncSession = Depends(get_async_session)
) -> User:  # нужно поменять модель (это огурец)
    user = await get_user(current_username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


async def get_access_from_refresh_token(
        token_service: TokenService = Depends(TokenService),
        current_user: dict = Depends(check_refresh_token),
        db: AsyncSession = Depends(get_async_session)
) -> str:
    'проверка refresh токена и создание accesss'
    await token_service.get_refresh_token_from_db_service(current_user['user_id'], db)

    access_token = create_access_token({
        'sub': current_user['username'],
        'uid': current_user['user_id']
    })

    return access_token

