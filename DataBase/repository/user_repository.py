import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.models import UserReturn, UserUpdate
from DataBase.repository.base_repository import BaseRepository
from DataBase.Shemas import UserDB


logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(UserDB, db)

    async def get_user_with_token_by_name_repo(self, username: str) -> UserDB | None:
        """возвращает юзера с токеном мо username"""
        try:

            result = await self.session.execute(
                select(UserDB).options(joinedload(UserDB.token)).where(UserDB.username == username)  # токен только один
            )
            logger.info("still for only one token")
            user = result.scalar_one_or_none()
            return user

        except Exception as e:
            logger.error(e)
            await self._handler_500(e, "get_user_with_token_by_name_repo")

    async def update_userinfo_repo(self, user_id: int, new_info: UserUpdate) -> UserReturn:
        """обновление информации о пользователе"""
        try:

            update_dict = new_info.model_dump(exclude_unset=True, exclude_none=True)
            query = update(UserDB).where(UserDB.id == user_id).values(**update_dict).returning(UserDB)

            result = await self.session.execute(query)
            await self.session.flush()
            new_user_data = result.scalar_one_or_none()
            return new_user_data

        except Exception as e:
            logger.error(e)
            await self._handler_500(e, "update_userinfo_repo")
