import time

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from DataBase.repository import check_user_exists, create_new_user
from app.exceptions import CustomException
from app.logger import logger
from app.models.models import UserCreate, UserTokenResponse
from app.services.hash_password import PasswordService
from app.services.token_service import TokenService
from auth.security import create_access_token, create_refresh_token


class UserService:
    def __init__(self):
        pass

    async def create_user_with_tokens(
            self,
            user: UserCreate,
            role: str,
            db: AsyncSession
    ) -> UserTokenResponse:
        """
        Полный цикл создания пользователя с токенами.
        rollback если где-то ошибка
        """
        try:
            token_service = TokenService()
            async with db.begin():

                if await check_user_exists(user.username, db):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Пользователь c таким именем уже существует"
                    )

                db_user = await create_new_user(
                    user=user,
                    role=role,
                    db=db
                )

                access_token = create_access_token({'sub': db_user.username})
                refresh_token = create_refresh_token({'sub': db_user.username})

                await db.flush()

                await token_service.save_refresh_token_in_db(
                    user_id=db_user.id,
                    token=refresh_token,
                    db_session=db
                )
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

    @staticmethod
    async def login_user(
            username: str,
            password: str,
            db: AsyncSession
    ):
        try:
            token_service = TokenService()
            password_service = PasswordService()
            async with db.begin():
                user = await check_user_exists(username=username, db=db)
                logger.debug(password)
                logger.debug(user.password)

                if not user:
                    logger.debug('User is %s', user)
                    raise CustomException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='wrong username or password',
                        message='на самом деле только юзер но не палим перед брут форсом'
                    )

                password_service.verify_password(password, user.password)

                access_token = create_access_token({'sub': username})
                refresh_token = create_refresh_token({'sub': username})
                logger.error('awdawdaw')

                await token_service.save_refresh_token_in_db(
                    user_id=user.id,
                    token=refresh_token,
                    db_session=db
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
