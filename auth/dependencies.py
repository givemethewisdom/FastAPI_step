from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User
from starlette import status

from DataBase.Database import get_async_session
from DataBase.repository import get_user
from auth.security import get_user_from_token


async def get_current_user(
    current_username: str = Depends(get_user_from_token),
    db: AsyncSession = Depends(get_async_session)  # Добавьте эту зависимость
) -> User:
    user = await get_user(current_username, db)  # Теперь передаем db
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
