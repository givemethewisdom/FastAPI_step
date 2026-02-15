import logging
import time

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.pickleable import User
from starlette import status

from DataBase.repository.user_repository import UserRepository
from app.exceptions import CustomException

from app.models.models import UserCreate, UserTokenResponse, UserReturn
from app.services.hash_password import PasswordService
from app.services.token_service import TokenService
from auth.security import create_access_token, create_refresh_token, decode_token

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository, token_service: TokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    async def get_current_user_from_token(self, token: str) -> UserReturn:
        """получает user info из любого токена"""
        user_info = await decode_token(token=token, token_type='access')
        res = await self.user_repo.get_obj_by_id(user_info['user_id'])
        if not res:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь не найден"
            )
        return res

    async def create_user_with_tokens_service(
            self,
            user: UserCreate,
            role: str
    ) -> UserTokenResponse:
        """
        Полный цикл создания пользователя с токенами.
        rollback если где-то ошибка
        """
        if await self.user_repo.get_user_with_token_by_name(user.username):
            # нужно заменить на проверку username хешсетом
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь c таким именем уже существует"
            )

        try:

            db_user = await self.user_repo.create_new_user(user=user, role=role)
            await self.user_repo.session.flush()

            # Создаём токены
            access_token = await create_access_token({
                'sub': db_user.username,
                'uid': db_user.id
            })
            refresh_token = await create_refresh_token({
                'sub': db_user.username,
                'uid': db_user.id
            })

            await self.token_service.save_refresh_token_in_db_service(
                user_id=db_user.id,
                token=refresh_token
            )

            await self.user_repo.session.commit()
            return UserTokenResponse(
                id=db_user.id,
                roles=role,
                username=db_user.username,
                info=db_user.info,
                access_token=access_token,
                refresh_token=refresh_token
            )

        except SQLAlchemyError as e:
            logger.error(e)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='server error',
                message='это из CustomException'
            )
        except HTTPException:
            # всякие HTTPException выше
            raise

    async def login_user_service(
            self,
            username: str,
            password: str
    ) -> UserTokenResponse:
        pass_service = PasswordService()
        try:
            user = await self.user_repo.get_user_with_token_by_name(username=username)

            if not user:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='wrong username or password',
                    message='на самом деле только юзер но не палим перед брут форсом'
                )

            if user.token.is_active is False:
                """по бизнес логике is_active False означает бан"""
                raise CustomException(
                    status_code=status.HTTP_410_GONE,
                    detail='token is inactive',
                    message='uк account was banned обратитесь к администратору'
                )
            # на самом деле можно проверять pass и токен в одной функции но пусть пока так
            await pass_service.verify_password(password, user.password)

            access_token = await create_access_token({
                'sub': username,
                'uid': user.id
            })
            logger.warning('Нужно протестить клейм uid в login_user!!!!!(я забыл что тестить)')
            refresh_token = await create_refresh_token({
                'sub': username,
                'uid': user.id
            })

            await self.token_service.save_refresh_token_in_db_service(
                user_id=user.id,
                token=refresh_token,
            )

            return UserTokenResponse(
                id=user.id,
                roles=user.roles,
                username=user.username,
                info=user.info,
                access_token=access_token,
                refresh_token=refresh_token
            )

        except SQLAlchemyError as e:
            logger.error(e)
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='server error',
                message='это из CustomException'
            )
        except HTTPException:
            # всякие HTTPException выше
            raise
