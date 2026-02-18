import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from DataBase.Shemas import UserDB
from DataBase.repository.base_repository import BaseRepository
from app.models.models import UserCreate, UserReturn, UserBase, UserUpdate
from app.services.hash_password import PasswordService

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(UserDB, db)

    async def get_user_with_token_by_name_repo(self, username: str) -> UserDB | None:
        """возвращает юзера с токеном мо username"""
        result = await self.session.execute(
            select(UserDB)
            .options(joinedload(UserDB.token))
            .where(UserDB.username == username)
        )
        logger.info('still for only one token')
        user = result.scalar_one_or_none()
        return user

    async def create_new_user_repo(self, user: UserCreate, role) -> UserDB:
        """
        Создать нового пользователя в БД.
        Возвращает SQLAlchemy модель UserDB.
        Не проверяет и не обрабатывает занятость username!!!
        """
        hashed_password = PasswordService.hash_password(user.password)#все еще хочу вернуть хеширования на уровень валидации
        # Создаем пользователя
        db_user = UserDB(
            username=user.username,
            password=hashed_password,
            info=user.info,
            roles=role
        )

        self.session.add(db_user)
        await self.session.flush()
        return db_user

    async def update_userinfo_repo(self,user_id: int, new_info:UserUpdate) -> UserReturn:
        """обновление информации о пользователе"""
        update_dict = new_info.model_dump(exclude_unset=True, exclude_none=True)
        query = (
            update(UserDB)
            .where(UserDB.id == user_id)
            .values(**update_dict)
            .returning(UserDB)
        )

        result = await self.session.execute(query)
        await self.session.flush()
        new_user_data = result.scalar_one_or_none()
        return new_user_data
