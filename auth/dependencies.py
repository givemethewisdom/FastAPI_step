from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User
from starlette import status

from DataBase.Database import get_async_session
from DataBase.repository import get_user
from app.logger import logger
from app.services.token_service import TokenService
from auth.security import create_access_token, decode_token, oauth2_scheme


def get_user_from_token(token: str = Depends(oauth2_scheme)) -> str:
    """DI-обёртка под FastAPI."""
    return decode_token(token)


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
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_async_session),
        token_service=Depends(TokenService)
) -> str:
    'проверка refresh токена и создание accesss'

    user_data = await token_service.check_refresh_token_service(token=token, db=db)

    access_token = create_access_token({
        'sub': user_data['username'],
        'uid': user_data['user_id']
    })

    return access_token
