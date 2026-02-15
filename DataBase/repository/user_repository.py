import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from DataBase.Shemas import UserDB
from DataBase.repository.base_repository import BaseRepository
from app.models.models import UserCreate
from app.services.hash_password import PasswordService

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(UserDB, db)

    async def get_user_with_token_by_name(self, username: str) -> UserDB | None:
        """возвращает юзера с токеном мо username"""
        result = await self.session.execute(
            select(UserDB)
            .options(joinedload(UserDB.token))
            .where(UserDB.username == username)
        )
        logger.info('still for only one token')
        user = result.scalar_one_or_none()
        return user

    async def create_new_user(self, user: UserCreate, role) -> UserDB:
        """
        Создать нового пользователя в БД.
        Возвращает SQLAlchemy модель UserDB.
        Не проверяет и не обрабатывает занятость username!!!
        """
        hashed_password = await PasswordService.hash_password(user.password)
        # Создаем пользователя
        db_user = UserDB(
            username=user.username,
            password=hashed_password,
            info=user.info,
            roles=role
        )

        self.session.add(db_user)
        return db_user
