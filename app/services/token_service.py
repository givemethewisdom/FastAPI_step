from datetime import timedelta, datetime, timezone
from typing import Dict

import jwt
from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.logger import logger
from app.models.models_token import RefreshTokenResponse
from auth.security import oauth2_scheme, SECRET_KEY, ALGORITHM, decode_refresh_token, create_access_token


class TokenService:
    def __init__(self):
        "взял просто с пароля"
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__time_cost=2,
            argon2__memory_cost=1024,
            argon2__parallelism=2,
        )

    def hash_token_service(self, token: str) -> str:
        """Хеширование токена"""
        return self.pwd_context.hash(token)

    def verify_token_service(self, token: str, token_hash: str) -> bool:
        """Проверка токена с хешем"""
        try:
            logger.debug('token %s, token_hash %s', token, token_hash)
            return self.pwd_context.verify(token, token_hash)
        except (ValueError, TypeError) as e:
            # Если хеш поврежден или неверного формата
            logger.error('verify_token_service has error: %s', e)
            raise

    async def save_refresh_token_in_db_service(
            self,
            user_id: int,
            token: str,
            db_session: AsyncSession,
    ):
        """Сохраняет refresh token в базу данных"""
        from DataBase.repository import save_refresh_token
        from auth.security import REFRESH_TOKEN_EXPIRE_MINUTES

        token_hash = self.hash_token_service(token)

        expire_at = datetime.now() + timedelta(REFRESH_TOKEN_EXPIRE_MINUTES)

        return await save_refresh_token(
            user_id=user_id,
            token_hash=token_hash,
            expire_at=expire_at,
            db=db_session
        )


    async def get_refresh_token_from_db_service(self, user_id: int, db_session: AsyncSession) -> RefreshTokenResponse:
        "получаем refresh token по user id"
        from DataBase.repository import get_refresh_token

        token = await get_refresh_token(user_id=user_id, db=db_session)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User have no any tokens"
            )

        if token.expires_at < datetime.now(tz=timezone.utc):
            # лучше навернео сразу удалять его но пусть будет
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Token has expired"
            )

        return token

    async def check_refresh_token_service(
            self,
            db: AsyncSession,
            token: str,
    ) -> dict:
        "проверяет валидность токена по типу refresh, отдает user_id: int(user_id),usernam: username"
        user_data = await decode_refresh_token(token=token)
        stored_token = await self.get_refresh_token_from_db_service(user_data['user_id'], db)
        self.verify_token_service(token=token, token_hash=stored_token.refresh_token)

        return user_data
