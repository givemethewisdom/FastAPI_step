from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.Shemas import TokenDB
from DataBase.repository.base_repository import BaseRepository


class TokenRepository(BaseRepository):
    """Репозиторий для токенов"""

    def __init__(self, session: AsyncSession):
        super().__init__(TokenDB, session)

    async def del_ref_token_by_user_id_repo(self, user_id: int) -> TokenDB | None:
        """удалить токен по user id"""
        obj = await self.session.execute(
            delete(TokenDB).where(TokenDB.user_id == user_id).returning(TokenDB)
        )
        res = obj.scalar_one_or_none()
        return res

    async def get_refresh_by_user_id_repo(self, user_id: int) -> TokenDB | None:
        """Получает токен по user_id"""
        query = select(TokenDB).where(TokenDB.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_refresh_token_repo(self, token_hash: str) -> None:
        """Удалить конкретный токен (скорее всего не нужно)"""
        await self.session.execute(
            delete(TokenDB).where(TokenDB.refresh_token == token_hash)
        )

    async def delete_all_user_tokens_repo(self, user_id: int) -> None:
        """Удалить все токены пользователя (скорее всего не нужно)"""
        await self.session.execute(
            delete(TokenDB).where(TokenDB.user_id == user_id)
        )

    async def deactivate_token_repo(self, user_id: int) -> None:
        """проверка в сервисе после flush!!!"""
        await self.session.execute(
            update(TokenDB)
            .where(TokenDB.user_id == user_id)
            .values(is_active=False)
        )
