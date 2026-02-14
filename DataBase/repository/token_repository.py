from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from DataBase.Shemas import TokenDB


class TokenRepository:
    """Репозиторий для токенов"""

    def __init__(self, session: AsyncSession):
        self.session = session

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

    async def get_active_token(self, user_id: int) -> TokenDB | None:
        """Получить активный токен пользователя"""
        query = select(TokenDB).where(
            TokenDB.user_id == user_id,
            TokenDB.expires_at > datetime.now()
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_token(self, token_hash: str) -> None:
        """Удалить конкретный токен"""
        await self.session.execute(
            delete(TokenDB).where(TokenDB.refresh_token == token_hash)
        )

    async def delete_all_user_tokens(self, user_id: int) -> None:
        """Удалить все токены пользователя"""
        await self.session.execute(
            delete(TokenDB).where(TokenDB.user_id == user_id)
        )