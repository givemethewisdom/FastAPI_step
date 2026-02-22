import logging

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from app.exceptions import CustomException
from app.models.models import UserCreate, UserReturn, UserTokenResponse, UserUpdate
from app.services.hash_password import PasswordService
from app.services.token_service import TokenService
from auth.security import create_access_token, create_refresh_token, decode_token
from DataBase.repository.user_repository import UserRepository


logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository, token_service: TokenService):
        self.user_repo = user_repo
        self.token_service = token_service

    async def get_user_serv(self, user_id: int):
        """get user by id"""
        user = await self.user_repo.get_obj_by_id_base_repo(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь c таким id не найден",
            )
        return user

    async def update_userinfo_serv(self, user_id: int, new_info: UserUpdate) -> UserReturn:
        """update username и info by id вместе с refresh токеном(admin privilege )"""
        # нужно вводить проверку username хеш-таблицей или т.п. и избавлять от проверок
        cur_username = await self.user_repo.get_user_with_token_by_name_repo(new_info.username)
        if cur_username:
            raise CustomException(
                status_code=status.HTTP_409_CONFLICT,
                detail="username already exists",
                message="try other one",
            )
        try:
            user = await self.user_repo.update_userinfo_repo(user_id, new_info)

            if not user:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="wrong user id",
                    message="user with this id does not exist",
                )

            ref_token = create_refresh_token({"sub": user.username, "uid": user.id})

            await self.token_service.save_refresh_token_in_db_service(user_id=user.id, token=ref_token)
            await self.user_repo.session.commit()
            return user
        except HTTPException:
            await self.user_repo.session.rollback()
            raise

        except Exception as e:
            await self.user_repo.session.rollback()
            logger.error("session rollback: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def get_current_user_from_token_serv(self, token: str) -> UserReturn:
        """получает user info из любого токена"""
        user_info = await decode_token(token=token, token_type="access")
        res = await self.user_repo.get_obj_by_id_base_repo(user_info["user_id"])
        if not res:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь не найден")
        return res

    async def create_user_with_tokens_service(self, user: UserCreate, role: str) -> UserTokenResponse:
        """
        Полный цикл создания пользователя с токенами.
        rollback если где-то ошибка
        """
        if await self.user_repo.get_user_with_token_by_name_repo(user.username):
            # нужно заменить на проверку username хешсетом
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь c таким именем уже существует",
            )
        hashed_password = PasswordService.hash_password(
            user.password
        )  # все еще хочу вернуть хеширования на уровень валидации

        try:
            db_user = await self.user_repo.create_obj_base_repo(
                username=user.username,
                password=hashed_password,
                info=user.info,
                roles=role,
            )

            # Создаём токены
            access_token = create_access_token({"sub": db_user.username, "uid": db_user.id})
            refresh_token = create_refresh_token({"sub": db_user.username, "uid": db_user.id})

            await self.token_service.save_refresh_token_in_db_service(user_id=db_user.id, token=refresh_token)

            await self.user_repo.session.commit()

            return UserTokenResponse(
                id=db_user.id,
                roles=role,
                username=db_user.username,
                info=db_user.info,
                access_token=access_token,
                refresh_token=refresh_token,
            )

        except Exception as e:
            await self.user_repo.session.rollback()
            logger.error(e)

    async def login_user_service(self, username: str, password: str) -> UserTokenResponse:
        pass_service = PasswordService()
        user = await self.user_repo.get_user_with_token_by_name_repo(username=username)

        if not user:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="wrong username or password",
                message="на самом деле только юзер но не палим перед брут форсом",
            )

        if user.token.is_active is False:
            """по бизнес логике is_active False означает бан"""
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="token is inactive",
                message="uк account was banned обратитесь к администратору",
            )
        # на самом деле можно проверять pass и токен в одной функции но пусть пока так
        pass_service.verify_password(password, user.password)

        access_token = create_access_token({"sub": username, "uid": user.id})
        logger.warning("Нужно протестить клейм uid в login_user!!!!!(я забыл что тестить)")
        refresh_token = create_refresh_token({"sub": username, "uid": user.id})

        await self.token_service.save_refresh_token_in_db_service(
            user_id=user.id,
            token=refresh_token,
        )
        try:
            await self.user_repo.session.commit()

            return UserTokenResponse(
                id=user.id,
                roles=user.roles,
                username=user.username,
                info=user.info,
                access_token=access_token,
                refresh_token=refresh_token,
            )

        except SQLAlchemyError as e:  # я не помню какие тут SQLAlchemyError но пока оставлю
            logger.error(e)
            await self.user_repo.session.rollback()
            raise CustomException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SQLAlchemyError",
                message="я не помню логику((",
            )
        except HTTPException:
            await self.user_repo.session.rollback()
            # всякие HTTPException выше
            raise

        except Exception:
            # для любого роллбак но я пошел спать
            await self.user_repo.session.rollback()
            raise

    async def delete_user_by_id_service(self, user_id: int) -> dict:
        """сервисм каскадное удаление user по id"""

        was_del = await self.user_repo.delete_obj_by_id_base_repo(user_id)

        if not was_del:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user with this id does not exist",
                message="make sure user exist",
            )

        try:

            await self.user_repo.session.commit()
            return {"success": "user deleted"}

        except Exception as e:
            # Неожиданные ошибки
            await self.user_repo.session.rollback()
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
