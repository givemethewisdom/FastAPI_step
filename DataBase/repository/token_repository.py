from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.Shemas import TokenDB
from DataBase.repository.base_repository import BaseRepository


class TokenRepository(BaseRepository):
    """Репозиторий для токенов"""

    def __init__(self, session: AsyncSession):
        super().__init__(TokenDB, session)

    async def save_refresh_token(self, user_id: int, token_hash: str, expire_at) -> TokenDB:
        """Сохранить refresh token (удаляя старый)"""
        await self.session.execute(
            delete(TokenDB).where(TokenDB.user_id == user_id)
        )

        db_token = TokenDB(
            user_id=user_id,
            refresh_token=token_hash,
            expires_at=expire_at,
        )
        self.session.add(db_token)
        return db_token

    async def get_refresh_token(self, user_id: int) -> TokenDB | None:
        """Получить токен без проверок"""
        query = select(TokenDB).where(
            TokenDB.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_refresh_by_user_id(self, user_id: int) -> TokenDB | None:
        """Получает токен по user_id"""
        query = select(TokenDB).where(TokenDB.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_refresh_token(self, token_hash: str) -> None:
        """Удалить конкретный токен (скорее всего не нужно)"""
        await self.session.execute(
            delete(TokenDB).where(TokenDB.refresh_token == token_hash)
        )

    async def delete_all_user_tokens(self, user_id: int) -> None:
        """Удалить все токены пользователя (скорее всего не нужно)"""
        await self.session.execute(
            delete(TokenDB).where(TokenDB.user_id == user_id)
        )

    async def deactivate_token(self, user_id: int) -> None:
        """проверка в сервисе после flush!!!"""
        await self.session.execute(
            update(TokenDB)
            .where(TokenDB.user_id == user_id)
            .values(is_active=False)
        )
