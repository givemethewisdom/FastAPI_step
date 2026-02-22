import logging
from typing import Any, Dict

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User
from starlette import status

from app.services.token_service import TokenService
from auth.security import create_access_token, decode_token, oauth2_scheme
from DataBase.Database import get_async_session
from DataBase.repository.repository import get_user


"""устаревший depends скорее всего нужно избавляться
используется только в about me"""
logger = logging.getLogger(__name__)


async def get_user_from_token(token: str = Depends(oauth2_scheme)) -> dict[str, int]:
    """DI-обёртка под FastAPI."""
    return await decode_token(token, "access")


async def get_current_user(
    current_use_info: dict = Depends(get_user_from_token), db: AsyncSession = Depends(get_async_session)
) -> User:  # нужно поменять модель (это огурец)
    user = await get_user(current_use_info["username"], db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
