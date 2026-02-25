"""вспомогательный сервис для user_service(может каких-то еще)
session.commit() НЕ ДЕЛАТЬ!!!"""

import logging
from datetime import datetime, timedelta, timezone

import passlib
from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status

from app.exceptions import CustomException
from app.models.models_token import RefreshTokenResponse
from auth.security import (
    REFRESH_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_token,
)
from DataBase.repository.token_repository import TokenRepository


logger = logging.getLogger(__name__)


class TokenService:
    def __init__(self, token_repo: TokenRepository):
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__time_cost=2,
            argon2__memory_cost=1024,
            argon2__parallelism=2,
        )
        self.token_repo = token_repo

    def hash_token_service(self, token: str) -> str:
        # нарушение DRY как-нибудь потом исправлю
        return self.pwd_context.hash(token)

    async def verify_token_service(self, token, token_hash: str) -> bool:
        """плохая логика (либо True либо CustomException Хотя  -> bool)
        но это пока не мешает"""
        try:
            bool_res = self.pwd_context.verify(token, token_hash)
            if not bool_res:
                logger.error("Token verification failed")
                raise CustomException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="invalid token",
                    message="try to log in again",
                )
            return bool_res

        except passlib.exc.UnknownHashError:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password",
                message="это поле вообще просто атк придумал не знаю что сюда писать",
            )

    async def save_refresh_token_in_db_service(
        self,
        user_id: int,
        token: str,
    ):
        """сохранить тоекен в БД (без комита)"""
        await self.token_repo.del_ref_token_by_user_id_repo(user_id)
        token_hash = self.hash_token_service(token)
        expire_at = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

        return await self.token_repo.create_obj_base_repo(
            user_id=user_id,
            refresh_token=token_hash,
            expires_at=expire_at,
        )

    async def make_token_access_via_refresh_service(self, refresh_token: str) -> str:
        "проверка refresh токена и создание accesss"
        user_data = await self.check_refresh_token_service(token=refresh_token)

        access_token = create_access_token({"sub": user_data["username"], "uid": user_data["user_id"]})

        return access_token

    async def get_refresh_token_from_db_service(self, user_id: int) -> RefreshTokenResponse:
        "получаем refresh token по user id"

        token = await self.token_repo.get_refresh_by_user_id_repo(user_id=user_id)

        if not token:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User have no any tokens")

        if not token.is_active:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Token is inactive")

        if token.expires_at < datetime.now(tz=timezone.utc):
            # лучше навернео сразу удалять его но пусть будет is_active = False
            # await self.token_repo.deactivate_token(user_id)
            # is_active будет в случае отстронения пользователя и не даст залогиниться
            # значит пусть просто логинится
            raise CustomException(
                status_code=status.HTTP_410_GONE,
                detail="Token has expired",
                message="u should LogIn again",
            )

        return token

    async def check_refresh_token_service(self, token: str) -> dict:
        "проверяет валидность токена по типу refresh, отдает user_id: int(user_id),usernam: username"
        user_data = await decode_token(token=token, token_type="refresh")
        stored_token = await self.get_refresh_token_from_db_service(user_data["user_id"])
        await self.verify_token_service(token=token, token_hash=stored_token.refresh_token)

        return user_data
